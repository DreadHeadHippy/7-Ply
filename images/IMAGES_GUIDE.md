# Trick Images Guide

## Directory Structure
```
images/
└── tricks/
    ├── regular/    # Regular stance screenshots
    └── goofy/      # Goofy stance screenshots
```

## File Naming Convention
- Use lowercase letters
- Replace spaces with underscores
- Use `.png` format
- Examples:
  - `kickflip.png`
  - `tre_flip.png`
  - `frontside_180.png`
  - `50-50_grind.png`

## Trick List for Screenshots

### Basic Tricks
- kickflip.png
- heelflip.png  
- ollie.png
- shuvit.png
- pop_shuvit.png

### Advanced Tricks
- varial_flip.png
- hardflip.png
- tre_flip.png
- nollie.png
- fakie_bigspin.png
- frontside_180.png
- backside_180.png

### Manuals
- manual.png
- nose_manual.png
- casper.png
- rail_stand.png

### Technical Tricks
- no_comply.png
- pogo.png
- disaster.png

### Grinds & Slides
- bluntslide.png
- lipslide.png
- boardslide.png
- 50-50_grind.png
- 5-0_grind.png
- nosegrind.png
- tailslide.png
- crooked_grind.png
- feeble_grind.png
- smith_grind.png
- darkslide.png
- casper_slide.png

## How to Add Images

1. Take screenshots of the Flick It control sequences from the game
2. Save them with the correct filename (see list above)
3. Place regular stance images in `images/tricks/regular/`
4. Place goofy stance images in `images/tricks/goofy/`
5. Use `/trickimages` command to check which ones are missing

## Bot Commands

- `/trick [stance]` - Show random trick with control image
- `/trickimages` - Check which images are available/missing (Admin only)
- `/tricklist` - See all available tricks

The bot will automatically detect and display your uploaded images when users use the `/trick` command!