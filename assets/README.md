# The right thread

`banner.gif` is an original Blucca route illustration: two source items move through a child workflow to their matching HTTP recipients. It illustrates the current n8n delivery work; it contains no activity counter or performance measurement.

The animation is a local raster asset, so GitHub can display its motion without an SVG script or a third-party image service. `banner-still.png` is the reduced-motion fallback in the Profile's `<picture>` element. Both use the same readable first composition.

Regenerate with `python3 assets/generate-banner.py` (Pillow + fonttools). The generator and its local Bricolage Grotesque / Instrument Sans font assets are included. Fonts retain the SIL Open Font License in `fonts/`. The original older `banner.svg` remains available for historical links.

The site uses the same route geometry as a native SVG, with a pause control and reduced-motion support. `--social /path/to/site/assets/studio/social.png` also writes its static sharing image.
