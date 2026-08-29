# Digital Residence exterior pipeline

Source `.blend` files stay in `assets-source/` (gitignored). This folder is the **tracked** generator.

## Blender

`C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`

## Rebuild

From the repo root:

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --python "tools\blender\digital-residence\build_exterior.py"
```

| Path                                                                      | Role              |
| ------------------------------------------------------------------------- | ----------------- |
| `assets-source/blender/digital-residence/DigitalResidence_Exterior.blend` | Private source    |
| `assets-source/blender/digital-residence/textures/`                       | Packed PBR images |
| `assets-source/blender/digital-residence/renders/`                        | Visual QA stills  |
| `public/assets/world/exterior/digital-residence-exterior.glb`             | Web runtime mesh  |

1 Blender unit = 1 meter. Naming follows `ENV_`, `PROP_`, `FX_`, `COL_`, `UI_`, `LIGHT_`, `CAM_`.

QA cameras: Hero Front, ThreeQuarter, Entrance, Side, Elevated, Material Detail, Gate/Boundary, Landscape, Night Wide, Web Preview.
