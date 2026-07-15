import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    // Hosts permitidos para evitar el bloqueo de Vite en entorno local/producción
    allowedHosts: ['sistema-de-trabajo-de-grado', 'localhost', '127.0.0.1'],
    // Permitir conexiones entrantes (útil en contenedores/VMs)
    host: true,
  },
})
