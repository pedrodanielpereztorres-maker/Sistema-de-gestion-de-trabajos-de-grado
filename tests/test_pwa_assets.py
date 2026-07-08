import json
from pathlib import Path


def test_manifest_uses_real_pwa_icons_from_assets_folder():
    project_root = Path(__file__).resolve().parents[1]
    manifest_path = project_root / "assets" / "iconos_sgtg_premium" / "manifest.json"

    assert (
        manifest_path.exists()
    ), "El manifiesto PWA debe existir en la carpeta de iconos"

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["start_url"] == "/"
    assert manifest["display"] == "standalone"
    assert manifest["theme_color"] == "#C9A84C"

    for icon in manifest["icons"]:
        assert icon["src"].startswith(
            "/iconos_sgtg_premium/"
        ), f"La ruta del icono debe apuntar a la carpeta de assets: {icon['src']}"
        asset_path = (
            project_root
            / "assets"
            / "iconos_sgtg_premium"
            / Path(icon["src"].split("/", 3)[-1])
        )
        assert asset_path.exists(), f"El icono referenciado no existe: {icon['src']}"
