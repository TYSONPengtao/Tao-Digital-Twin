TAO Demo House v0.1
===================

Files:
- demo-house.glb                Generated and validated runtime GLB for Three.js.
- demo-house-manifest.json      Room/device mapping and default simulated states.
- build_demo_house_blender.py   Blender Python source generator.

The current ChatGPT runtime does not include Blender, so it cannot serialize a native .blend file directly.
On a PC with Blender installed, place build_demo_house_blender.py in a folder and run:

  blender --background --python build_demo_house_blender.py

This creates:
- demo-house.blend
- demo-house-from-blender.glb

Main interactive device node names:
- DEV_Light_Living_Main
- DEV_TV_Living
- DEV_Curtain_Living
- DEV_Light_Bedroom
- DEV_AC_Bedroom
- DEV_Light_Kitchen
- DEV_SmokeSensor_Kitchen
- DEV_Irrigation_Balcony

Model scale: meters
Approximate footprint: 12m x 8m x 2.8m
