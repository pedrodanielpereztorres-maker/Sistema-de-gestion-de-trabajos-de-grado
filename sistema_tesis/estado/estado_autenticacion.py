import asyncio
import logging
import reflex as rx
from reflex import Cookie
from pydantic import BaseModel
import bcrypt
import secrets
from datetime import datetime, timedelta, timezone
from ..database_manager import obtener_conexion

# En producción asegúrate que el nivel sea INFO o superior
# Nunca configures basicConfig con DEBUG en el servidor
logger = logging.getLogger(__name__)

class EncriptadorContrasena:
    MAX_BYTES_CONTRASENA = 72

    @staticmethod
    def _verificar_longitud(contrasena: str):
        if len(contrasena.encode("utf-8")) > EncriptadorContrasena.MAX_BYTES_CONTRASENA:
            raise ValueError("La contraseña es demasiado larga.")

    @staticmethod
    def encriptar(contrasena: str) -> str:
        EncriptadorContrasena._verificar_longitud(contrasena)
        sal = bcrypt.gensalt()
        return bcrypt.hashpw(contrasena.encode("utf-8"), sal).decode("utf-8")

    @staticmethod
    def verificar(contrasena: str, hash_almacenado: str) -> bool:
        try:
            if not contrasena or not hash_almacenado:
                return False
            EncriptadorContrasena._verificar_longitud(contrasena)
            return bcrypt.checkpw(
                contrasena.encode("utf-8"),
                hash_almacenado.strip().encode("utf-8")
            )
        except Exception:
            logger.error("Error en verificación de hash.")
            return False

class Usuario(BaseModel):
    id: int | None = None
    nombre_usuario: str = ""
    rol: str = ""
    nombre_completo: str = ""
    cedula: str = ""
    correo: str = ""
    token_sesion: str | None = None

class EstadoAutenticacion(rx.State):
    usuario: Usuario | None = None
    entrada_usuario: str = ""
    entrada_contrasena: str = ""
    token_cookie: Cookie | str = ""
    
    # Rate Limiting (Tarea 5)
    intentos_fallidos: int = 0
    bloqueado_hasta: str = ""  # ISO datetime string
    mostrar_contrasena: bool = False

    def alternar_mostrar_contrasena(self):
        self.mostrar_contrasena = not self.mostrar_contrasena

    @rx.var
    def nombre_usuario(self) -> str:
        return self.usuario.nombre_completo if self.usuario else "Invitado"

    @rx.var
    def inicial_usuario(self) -> str:
        return self.nombre_usuario[0].upper() if self.usuario else "I"

    @rx.var
    def rol_usuario(self) -> str:
        return self.usuario.rol.lower() if self.usuario else "invitado"

    @rx.var
    def usuario_id(self) -> int:
        return int(self.usuario.id) if self.usuario and self.usuario.id is not None else 0

    @rx.var
    def token_actual(self) -> str:
        if self.usuario and self.usuario.token_sesion:
            return self.usuario.token_sesion
        return str(self.token_cookie or "")

    async def restaurar_sesion(self):
        if self.usuario and self.usuario.token_sesion:
            return

        token = str(self.token_cookie or "")
        if not token:
            return

        def _fetch_session(token_val: str):
            conn2 = obtener_conexion()
            if conn2 is None:
                return None
            try:
                with conn2:
                    with conn2.cursor() as cursor:
                        cursor.execute(
                            """
                            SELECT u.id, u.cedula, u.nombre, u.apellido, u.correo, r.nombre
                            FROM sesion s
                            JOIN usuario u ON u.id = s.usuario_id
                            LEFT JOIN rol r ON u.rol_id = r.id
                            WHERE s.token = %s AND s.esta_activa = TRUE AND s.expira_en > NOW();
                            """,
                            (token_val,),
                        )
                        return cursor.fetchone()
            except Exception as exc:
                logger.error("Error al restaurar sesión: %s", exc, exc_info=True)
                return None
            finally:
                try:
                    conn2.close()
                except Exception:
                    pass

        resultado = await asyncio.to_thread(_fetch_session, token)
        if resultado:
            u_id, u_ced, u_nom, u_ape, u_cor, u_rol = resultado
            self.usuario = Usuario(
                id=u_id,
                nombre_usuario=u_cor,
                rol=u_rol.lower() if u_rol else "estudiante",
                nombre_completo=f"{u_nom} {u_ape}",
                cedula=u_ced,
                correo=u_cor,
                token_sesion=token,
            )

    def iniciar_sesion(self):
        # 1. Verificar bloqueo por Rate Limiting
        if self.bloqueado_hasta:
            limite = datetime.fromisoformat(self.bloqueado_hasta)
            ahora = datetime.now(timezone.utc)
            if ahora < limite:
                segundos = int((limite - ahora).total_seconds())
                return rx.toast.error(f"⚠️ Acceso Bloqueado: Has realizado demasiados intentos de inicio de sesión. Por motivos de seguridad, por favor espera {segundos} segundos antes de volver a intentar.")
            else:
                self.bloqueado_hasta = ""
                self.intentos_fallidos = 0

        correo_entrada = self.entrada_usuario.strip().lower()

        resultado, error = self._fetch_user_by_email(correo_entrada)
        if error:
            return rx.toast.error(error)

        if resultado:
            u_id, u_ced, u_nom, u_ape, u_cor, u_hash, u_act, u_rol = resultado
            if not u_act:
                return rx.toast.error("🔒 Cuenta Desactivada: Su cuenta de usuario ha sido desactivada por el administrador del sistema. Por favor, solicite asistencia para reactivarla.")

            if EncriptadorContrasena.verificar(self.entrada_contrasena, u_hash):
                token = secrets.token_urlsafe(64)
                ahora_utc = datetime.now(timezone.utc)

                if not self._create_session(u_id, token, ahora_utc, ahora_utc + timedelta(hours=24)):
                    return rx.toast.error("💥 Error Crítico: No se pudo iniciar la sesión en el servidor. Reintente más tarde.")

                self.intentos_fallidos = 0
                self.bloqueado_hasta = ""
                self.usuario = Usuario(
                    id=u_id,
                    nombre_usuario=u_cor,
                    rol=u_rol.lower() if u_rol else "estudiante",
                    nombre_completo=f"{u_nom} {u_ape}",
                    cedula=u_ced,
                    correo=u_cor,
                    token_sesion=token,
                )
                self.token_cookie = token
                self.entrada_contrasena = ""
                logger.debug("Sesión creada exitosamente.")
                return rx.redirect("/")

        self.intentos_fallidos += 1
        if self.intentos_fallidos >= 5:
            self.bloqueado_hasta = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
            return rx.toast.error("⚠️ Seguridad: Demasiados intentos fallidos consecutivos. Su cuenta ha sido bloqueada temporalmente por un lapso de 5 minutos.")
        return rx.toast.error("❌ Credenciales Incorrectas: El correo electrónico o la contraseña ingresados no coinciden con ningún registro activo.")

    def _fetch_user_by_email(self, email: str):
        conn2 = obtener_conexion()
        if conn2 is None:
            return None, "🔌 Fallo de Conexión: No se pudo establecer comunicación con el servidor de la base de datos. Compruebe su conexión de red o contacte al administrador."
        try:
            with conn2:
                with conn2.cursor() as cursor:
                    logger.debug("Intento de login recibido.")
                    cursor.execute("""
                        SELECT u.id, u.cedula, u.nombre, u.apellido, u.correo, u.contrasena_hash, u.esta_activo, r.nombre
                        FROM usuario u
                        LEFT JOIN rol r ON u.rol_id = r.id
                        WHERE LOWER(TRIM(u.correo)) = %s;
                    """, (email,))
                    resultado = cursor.fetchone()
                    return resultado, ""
        except Exception as exc:
            logger.error(f"Error en login: {exc}", exc_info=True)
            return None, "💥 Error Crítico: Ocurrió una anomalía interna en el sistema al intentar procesar su solicitud. Por favor, reintente más tarde o reporte este evento a soporte."
        finally:
            try:
                conn2.close()
            except Exception:
                pass

    def _create_session(self, user_id: int, token_val: str, creado: datetime, expira: datetime):
        conn3 = obtener_conexion()
        if conn3 is None:
            return False
        try:
            with conn3:
                with conn3.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO sesion (usuario_id, token, creado_en, expira_en, esta_activa)
                        VALUES (%s, %s, %s, %s, TRUE);
                    """, (user_id, token_val, creado, expira))
                conn3.commit()
            return True
        except Exception as exc:
            logger.error(f"Error al crear sesión: {exc}", exc_info=True)
            return False
        finally:
            try:
                conn3.close()
            except Exception:
                pass

    async def cerrar_sesion(self):
        if self.usuario and self.usuario.token_sesion:
            def _deactivate_session(token: str):
                conn2 = obtener_conexion()
                if conn2 is None:
                    return False
                try:
                    with conn2:
                        with conn2.cursor() as cursor:
                            cursor.execute("UPDATE sesion SET esta_activa = FALSE WHERE token = %s", (token,))
                        conn2.commit()
                    return True
                except Exception as exc:
                    logger.error(f"Error al cerrar sesión: {exc}", exc_info=True)
                    return False
                finally:
                    try:
                        conn2.close()
                    except Exception:
                        pass

            await asyncio.to_thread(_deactivate_session, self.usuario.token_sesion)
        self.token_cookie = ""
        self.reset()
        return rx.redirect("/login")

    async def verificar_sesion(self):
        await self.restaurar_sesion()
        if self.usuario is None:
            return rx.redirect("/login")

    async def verificar_sesion_admin(self):
        await self.restaurar_sesion()
        if self.usuario is None:
            return rx.redirect("/login")
        if self.rol_usuario != 'administrador':
            return rx.redirect("/")

    # Compatibilidad: alias de nombres históricos usados en las páginas
    async def verificar_acceso(self):
        """Alias histórico para verificar sesión de usuario (mantiene compatibilidad).

        Antes se llamaba verificar_acceso desde on_mount en varias páginas; ahora
        verificamos sesión usando el método moderno verificar_sesion.
        """
        await self.verificar_sesion()

    async def verificar_acceso_admin(self):
        """Alias histórico para verificar acceso de administrador."""
        await self.verificar_sesion_admin()

    def fijar_entrada_usuario(self, val): self.entrada_usuario = val
    def fijar_entrada_contrasena(self, val): self.entrada_contrasena = val
