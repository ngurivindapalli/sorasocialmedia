# Backup Files - Falling Posts Gallery

This directory contains backup files for the working version of the FallingPostsGallery component.

## Files:

1. **`frontend/src/components/FallingPostsGallery.backup.jsx`**
   - Working version with:
     - 4 posts displayed at positions [0, 25, 50, 65]% (prevents right-side cutoff)
     - 20 second animation duration
     - Proper initial delay distribution
     - 300px image size
     - Scale 0.8-0.9 for professional look

2. **`frontend/src/App.css.backup`**
   - Animation keyframes with:
     - Images fall to 160% (further down)
     - Fade starts at 95% (stays visible longer)
     - Starts at -30% translateY

## To Restore:

1. Copy `FallingPostsGallery.backup.jsx` to `FallingPostsGallery.jsx`
2. Copy the `@keyframes fall` section from `App.css.backup` to `App.css`

## Current Features:
- ✅ 4 posts visible at a time
- ✅ No right-side cutoff (max 65% position)
- ✅ Images fall further (160% translateY)
- ✅ Images stay visible longer (fade at 95%)
- ✅ Proper staggered delays
- ✅ Professional spacing and scaling


