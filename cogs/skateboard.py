"""
Skateboard Commands Cog
Contains all skateboarding-related slash commands
"""

import random
import discord
from discord.ext import commands
from discord import app_commands
import os
import io
import aiohttp
import datetime
import pytz
from utils.security import SecurityValidator, SecureError

SKATE_TRICKS = [
    "Kickflip", "Heelflip", "Ollie", "Shuvit", "Pop Shuvit", "Varial Kickflip", "Varial Heelflip", "Hardflip", "360 Flip",
    "Laserflip", "360 Pop Shuvit", "Inward Heelflip", "Nollie", "Fakie Bigspin", "Frontside 180", "Backside 180", "Manual", "Nose Manual",
    "Rail Stand", "No Comply", "Bluntslide", "Lipslide", "Boardslide", "50-50 Grind",
    "5-0 Grind", "Nosegrind", "Tailslide", "Crooked Grind", "Feeble Grind", "Smith Grind"
]

# Custom tips and facts for specific tricks
TRICK_TIPS = {
    "360 Flip": {
        "name": "💯 Fact",
        "value": '360 Flips are also known as treflips.'
    },
    "Laserflip": {
        "name": "💯 Fact", 
        "value": "Laserflips are also known as 360 Heelflips."
    },
    "Kickflip": {
        "name": "💯 Fact",
        "value": 'The kickflip was originally called a "magic flip" when it was invented.'
    },
    "Ollie": {
        "name": "💯 Fact",
        "value": 'The ollie was invented by Alan "Ollie" Gelfand in 1978 and is the foundation of all skateboard tricks.'
    },
    "Hardflip": {
        "name": "💡 Pro Tip",
        "value": "Hardflips combine a heelflip with a frontside shuvit - master both tricks separately first!"
    },
    "Varial Kickflip": {
        "name": "💡 Pro Tip", 
        "value": "Varial kickflips combine a kickflip with a shuvit - practice the scoop and flick timing together."
    },
    "Inward Heelflip": {
        "name": "💡 Pro Tip",
        "value": "Inward heelflips rotate opposite to regular heelflips - use your toe to flick inward instead of heel out."
    }
}

SKATE_FACTS = [
    "The first skateboards were made in the 1940s by attaching roller skate wheels to wooden planks.",
    "The ollie was invented by Alan \"Ollie\" Gelfand in 1978.",
    "Skateboarding was banned in Norway from 1978 to 1989.",
    "Tony Hawk landed the first ever 900 in competition in 1999.",
    "The longest manual ever recorded is over 2 miles!",
    "Skateboarding made its Olympic debut in Tokyo 2020.",
    "Grip tape was inspired by sandpaper.",
    "The kickflip was originally called a 'magic flip'.",
    "Vans was the first company to make shoes specifically for skateboarding.",
    "The X-Games started in 1995 and helped popularize skateboarding worldwide.",
    "Street skating developed in the 1980s when skaters started using urban obstacles.",
    "The first skate video was 'Skateboard Kings' released in 1978.",
    "Rodney Mullen is often called the 'Godfather of Street Skating'.",
    "Skateboard decks are typically made from 7-ply maple wood.",
    "The skateboard truck was invented in 1962 by Bill Richards."
]

# Skateboard brand database - from legends to modern day
SKATE_BRANDS = [
    {
        "name": "Powell Peralta",
        "founded": "1976",
        "location": "Santa Barbara, California",
        "status": "Active",
        "description": "Legendary brand that defined 80s skateboarding with iconic graphics and team riders.",
        "notable": "Bones Brigade team, iconic skull graphics, and pioneering skateboard videos",
        "fun_fact": "Their 'Bones Brigade Video Show' (1984) revolutionized skate videos forever."
    },
    {
        "name": "Santa Cruz Skateboards",
        "founded": "1973",
        "location": "Santa Cruz, California", 
        "status": "Active (oldest continuous skateboard company)",
        "description": "The oldest continuously operating skateboard company in the world.",
        "notable": "Screaming Hand logo, Jim Phillips artwork, and 50+ years of history",
        "fun_fact": "The Screaming Hand logo was created in 1985 and became skateboarding's most iconic graphic."
    },
    {
        "name": "Thrasher Magazine",
        "founded": "1981",
        "location": "San Francisco, California",
        "status": "Active",
        "description": "The skateboard magazine that became a lifestyle brand and cultural icon.",
        "notable": "Skater of the Year awards, 'Thrasher' logo apparel, and raw skate coverage",
        "fun_fact": "Their flame logo is now worn by celebrities who've probably never touched a skateboard."
    },
    {
        "name": "Vans",
        "founded": "1966",
        "location": "Anaheim, California",
        "status": "Active (now owned by VF Corporation)",
        "description": "The first company to make shoes specifically designed for skateboarding.",
        "notable": "Waffle sole grip, Era and Old Skool models, and 'Off The Wall' slogan",
        "fun_fact": "Stacy Peralta convinced Vans to sponsor the Z-Boys, launching skate shoe culture."
    },
    {
        "name": "Independent Truck Company",
        "founded": "1978",
        "location": "Santa Cruz, California",
        "status": "Active", 
        "description": "The most respected truck manufacturer in skateboarding history.",
        "notable": "Forged baseplate technology, cross logo, and rider-owned company",
        "fun_fact": "The 'Indy' cross logo tattoo is like a badge of honor in the skate community."
    },
    {
        "name": "Dogtown Skateboards",
        "founded": "1976",
        "location": "Venice, California",
        "status": "Active (reformed multiple times)",
        "description": "The brand that emerged from the legendary Z-Boys crew of Venice Beach.",
        "notable": "Z-Boys team, aggressive pool riding style, and Venice Beach culture",
        "fun_fact": "The original DT logo was designed by Craig Stecyk and became a symbol of rebellion."
    },
    {
        "name": "World Industries",
        "founded": "1987",
        "location": "Los Angeles, California",
        "status": "Defunct (sold 2002)",
        "defunct": True,
        "description": "Steve Rocco's controversial company that changed skateboard marketing forever.",
        "notable": "Flame Boy logo, aggressive advertising, and poaching top pros from other brands",
        "fun_fact": "Steve Rocco's guerrilla marketing tactics were so wild they made enemies of every major brand."
    },
    {
        "name": "Vision Street Wear",
        "founded": "1976",
        "location": "Los Angeles, California",
        "status": "Defunct (original run ended early 90s)",
        "defunct": True,
        "description": "80s skateboard company that also pioneered skate fashion and streetwear.",
        "notable": "Gator team rider, neon graphics, and crossover into mainstream fashion",
        "fun_fact": "They were one of the first to realize skateboarding could sell lifestyle, not just equipment."
    },
    {
        "name": "Hosoi Skateboards",
        "founded": "1982",
        "location": "California",
        "status": "Active (reformed)",
        "description": "Christian Hosoi's signature brand known for vert skateboarding excellence.",
        "notable": "Hammerhead shape, vert pool riding, and Hosoi's legendary style",
        "fun_fact": "The Hammerhead shape was revolutionary for transition skating and pool riding."
    },
    {
        "name": "Plan B Skateboards", 
        "founded": "1991",
        "location": "San Diego, California",
        "status": "Active (reformed multiple times)",
        "description": "Technical street skating company co-founded by Mike Ternasky and Danny Way.",
        "notable": "Questionable video (1992), technical street innovation, and legendary team",
        "fun_fact": "Plan B's 'Questionable' video literally questioned everything about skateboarding at the time."
    },
    {
        "name": "Flip Skateboards",
        "founded": "1991", 
        "location": "Huntington Beach, California",
        "status": "Active",
        "description": "Technical street skateboarding company known for innovation and progression.",
        "notable": "Sorry video series, technical wizardry, and European influence",
        "fun_fact": "Geoff Rowley's part in 'Sorry' redefined what was possible in street skating."
    },
    {
        "name": "Girl Skateboards",
        "founded": "1993",
        "location": "Los Angeles, California", 
        "status": "Active",
        "description": "Rick Howard and Mike Carroll's company focused on style and creativity.",
        "notable": "Clean graphics, Mouse video (1996), and effortless style approach",
        "fun_fact": "The 'Mouse' video showed that skateboarding could be artistic without losing its edge."
    },
    {
        "name": "Baker Skateboards",
        "founded": "2000",
        "location": "Los Angeles, California",
        "status": "Active", 
        "description": "Andrew Reynolds' raw, underground approach to skateboarding and videos.",
        "notable": "Baker Boys distribution, grimy aesthetic, and East Coast influence",
        "fun_fact": "Baker's 'bootleg' video aesthetic influenced a whole generation of filmers."
    },
    {
        "name": "Supreme",
        "founded": "1994",
        "location": "New York City, New York",
        "status": "Active (sold to VF Corp 2020)",
        "description": "NYC skateshop that became a global streetwear phenomenon.",
        "notable": "Box logo, limited drops, and bridging skate culture with high fashion",
        "fun_fact": "What started as a small skate shop now has people camping out for $300 t-shirts."
    },
    {
        "name": "Alien Workshop",
        "founded": "1990",
        "location": "Dayton, Ohio",
        "status": "Defunct (closed 2014)", 
        "defunct": True,
        "description": "Midwest skateboard company known for artistic graphics and creative videos.",
        "notable": "Abstract art graphics, Photosynthesis video, and East Coast representation",
        "fun_fact": "Their graphics were so artistic that museums started collecting their boards as art pieces."
    },
    {
        "name": "Element Skateboards",
        "founded": "1992",
        "location": "Irvine, California",
        "status": "Active",
        "description": "Nature-inspired skateboard company emphasizing environmental consciousness.",
        "notable": "Tree logo, Bam Margera sponsorship, and eco-friendly initiatives",
        "fun_fact": "They were pushing environmental awareness in skateboarding way before it was trendy."
    },
    {
        "name": "Zero Skateboards",
        "founded": "1996",
        "location": "Carlsbad, California",
        "status": "Active",
        "description": "Jamie Thomas' hardcore approach to skateboarding with heavy metal influence.",
        "notable": "Skull graphics, gnarly street skating, and 'Chief' Jamie Thomas leadership",
        "fun_fact": "Jamie Thomas earned the nickname 'The Chief' for his leadership and massive stair sets."
    },
    {
        "name": "Toy Machine",
        "founded": "1993", 
        "location": "San Diego, California",
        "status": "Active",
        "description": "Ed Templeton's artistic skateboard company blending art with skateboarding.",
        "notable": "Templeton's photography/art, sect logo, and creative approach",
        "fun_fact": "Ed Templeton is a respected contemporary artist whose work is displayed in major galleries."
    },
    {
        "name": "Spitfire Wheels",
        "founded": "1987",
        "location": "San Francisco, California", 
        "status": "Active",
        "description": "Premium skateboard wheel company known for quality and performance.",
        "notable": "Bighead logo, Formula Four wheels, and consistent quality",
        "fun_fact": "The Spitfire Bighead is one of the most recognizable logos in all of skateboarding."
    },
    {
        "name": "Bones Bearings",
        "founded": "1981",
        "location": "Santa Barbara, California",
        "status": "Active",
        "description": "The gold standard for skateboard bearings and precision engineering.",
        "notable": "Swiss bearings, precision engineering, and industry standard quality",
        "fun_fact": "Bones Swiss bearings cost more than most complete skateboards but pros swear by them."
    }
]

class SkateboardCommands(commands.Cog):
    """Skateboarding-related commands"""
    
    def __init__(self, bot):
        self.bot = bot
        # EDT timezone
        self.edt = pytz.timezone('America/New_York')
    
    def get_edt_now(self) -> datetime.datetime:
        """Get current time in EDT"""
        return datetime.datetime.now(self.edt)
    
    async def award_trick_points(self, user_id: int):
        """Award points for using trick commands"""
        try:
            ranking_cog = self.bot.get_cog('RankingSystem')
            if ranking_cog:
                points, ranked_up = ranking_cog.award_points(user_id, "trick_command")
                return points, ranked_up
        except Exception as e:
            print(f"Error awarding trick points: {e}")
        return 0, False

    @app_commands.command(name='trick', description='Get a random skateboarding trick with Flick It controls!')
    async def trick(self, interaction: discord.Interaction):
        """Get a random skateboarding trick to practice with Flick It control images for both stances"""
        
        # Award points for using the command
        await self.award_trick_points(interaction.user.id)
        
        trick = random.choice(SKATE_TRICKS)
        
        embed = discord.Embed(
            title="🛹 Random Trick Challenge!",
            description=f"**{trick}**",
            color=0x00ff00
        )
        
        # Use custom tip if available, otherwise use default
        if trick in TRICK_TIPS:
            tip_data = TRICK_TIPS[trick]
            embed.add_field(
                name=tip_data["name"],
                value=tip_data["value"],
                inline=False
            )
        else:
            embed.add_field(
                name="💡 Tip", 
                value="Practice makes perfect! Start with the basics and work your way up.", 
                inline=False
            )
        
        # Check for control sequence images 
        files = []
        top_right_image = None  # Thumbnail position
        bottom_image = None     # Main image position
        image_type = ""
        
        # Clean trick name for filename (remove spaces, special chars)
        clean_trick = "".join(c for c in trick if c.isalnum() or c in (' ', '-')).rstrip()
        clean_trick = clean_trick.replace(' ', '_').lower()
        
        # Debug: Add this temporarily to see what's happening
        print(f"DEBUG: Trick='{trick}', Clean='{clean_trick}'")
        print(f"DEBUG: Current working directory: {os.getcwd()}")
        
        # Check for both PNG and JPG formats
        image_extensions = ['.png', '.jpg', '.jpeg']
        
        # Determine trick type and find images
        grind_slide_keywords = ['grind', 'slide', 'blunt', 'lipslide', 'boardslide', '50-50', '5-0', 'nosegrind', 'tailslide', 'crooked', 'feeble', 'smith']
        is_grind_slide = any(keyword in trick.lower() for keyword in grind_slide_keywords)
        
        # Initialize variables
        files = []
        top_right_image = None
        bottom_image = None
        image_type = ""
        
        try:
            print(f"DEBUG: Starting image detection for '{clean_trick}'")
            
            # Special tricks that have single images in the main tricks folder
            single_image_tricks = ['manual', 'no comply', 'nose manual', 'rail stand']
            is_single_image = any(single_trick in trick.lower() for single_trick in single_image_tricks)
            print(f"DEBUG: is_single_image = {is_single_image}")
            
            if is_single_image:
                print(f"DEBUG: Processing single image trick")
                # Look for single image in main tricks folder
                for ext in image_extensions:
                    single_path = f"images/tricks/{clean_trick}{ext}"
                    if os.path.exists(single_path):
                        single_filename = f"{clean_trick}{ext}"
                        bottom_image = discord.File(single_path, filename=single_filename)
                        files.append(bottom_image)
                        break
                
                image_type = "single"
            elif is_grind_slide:
                print(f"DEBUG: Processing grind/slide trick")
                
                # Clean grind name by removing common suffixes
                grind_name = clean_trick.replace('_grind', '').replace('_slide', '')
                print(f"DEBUG: Cleaned grind name: '{grind_name}'")
                
                # Look for frontside image (goes top-right like regular stance)
                for ext in image_extensions:
                    fs_path = f"images/tricks/grinds/fs_{grind_name}{ext}"
                    print(f"DEBUG: Checking frontside path: {fs_path}")
                    print(f"DEBUG: File exists: {os.path.exists(fs_path)}")
                    if os.path.exists(fs_path):
                        fs_filename = f"fs_{grind_name}{ext}"
                        top_right_image = discord.File(fs_path, filename=fs_filename)
                        files.append(top_right_image)
                        print(f"DEBUG: Found frontside image: {fs_path}")
                        break
                
                # Look for backside image (goes bottom like goofy stance)
                for ext in image_extensions:
                    bs_path = f"images/tricks/grinds/bs_{grind_name}{ext}"
                    print(f"DEBUG: Checking backside path: {bs_path}")
                    print(f"DEBUG: File exists: {os.path.exists(bs_path)}")
                    if os.path.exists(bs_path):
                        bs_filename = f"bs_{grind_name}{ext}"
                        bottom_image = discord.File(bs_path, filename=bs_filename)
                        files.append(bottom_image)
                        print(f"DEBUG: Found backside image: {bs_path}")
                        break
                
                image_type = "grind"
            else:
                print(f"DEBUG: Processing regular/goofy stance trick")
                # Look for regular stance image (goes top-right)
                for ext in image_extensions:
                    regular_path = f"images/tricks/regular/{clean_trick}{ext}"
                    print(f"DEBUG: Checking regular path: {regular_path}")
                    print(f"DEBUG: File exists: {os.path.exists(regular_path)}")
                    if os.path.exists(regular_path):
                        regular_filename = f"{clean_trick}_regular{ext}"
                        top_right_image = discord.File(regular_path, filename=regular_filename)
                        files.append(top_right_image)
                        print(f"DEBUG: Found regular image: {regular_path}")
                        break
                
                # Look for goofy stance image (goes bottom)
                for ext in image_extensions:
                    goofy_path = f"images/tricks/goofy/{clean_trick}{ext}"
                    print(f"DEBUG: Checking goofy path: {goofy_path}")
                    print(f"DEBUG: File exists: {os.path.exists(goofy_path)}")
                    if os.path.exists(goofy_path):
                        goofy_filename = f"{clean_trick}_goofy{ext}"
                        bottom_image = discord.File(goofy_path, filename=goofy_filename)
                        files.append(bottom_image)
                        print(f"DEBUG: Found goofy image: {goofy_path}")
                        break
                
                image_type = "stance"
        
        except Exception as e:
            print(f"DEBUG: Exception during image detection: {e}")
            print(f"DEBUG: Exception type: {type(e).__name__}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            files = []
            top_right_image = None
            bottom_image = None
            image_type = ""
        
        # Set images in embed (top-right image as thumbnail, bottom image as main)
        if top_right_image:
            embed.set_thumbnail(url=f"attachment://{top_right_image.filename}")
        
        if bottom_image:
            embed.set_image(url=f"attachment://{bottom_image.filename}")
        
        # Update the control info based on what images we have and trick type
        if top_right_image and bottom_image:
            if image_type == "grind":
                embed.add_field(
                    name="🎮 Flick It Controls",
                    value="**Frontside** - Thumbnail (top-right)\n**Backside** - Main image (below)",
                    inline=False
                )
            else:
                embed.add_field(
                    name="🎮 Flick It Controls",
                    value="**Regular Stance** - Thumbnail (top-right)\n**Goofy Stance** - Main image (below)",
                    inline=False
                )
        elif top_right_image:
            if image_type == "grind":
                embed.add_field(
                    name="🎮 Flick It Controls", 
                    value="**Frontside** - See thumbnail (top-right)\n*(Backside image coming soon)*",
                    inline=False
                )
            else:
                embed.add_field(
                    name="🎮 Flick It Controls", 
                    value="**Regular Stance** - See thumbnail (top-right)\n*(Goofy stance image coming soon)*",
                    inline=False
                )
        elif bottom_image:
            if image_type == "grind":
                embed.add_field(
                    name="🎮 Flick It Controls",
                    value="**Backside** - See main image (below)\n*(Frontside image coming soon)*", 
                    inline=False
                )
            elif image_type == "single":
                embed.add_field(
                    name="🎮 Flick It Controls",
                    value="**Control sequence** - See image below", 
                    inline=False
                )
            else:
                embed.add_field(
                    name="🎮 Flick It Controls",
                    value="**Goofy Stance** - See main image (below)\n*(Regular stance image coming soon)*", 
                    inline=False
                )
        else:
            embed.add_field(
                name="🎮 Flick It Controls",
                value="Control sequence images coming soon! 📸\nUpload screenshots to show the control sequences.",
                inline=False
            )
        
        embed.set_footer(text="Keep shredding! 🤙")
        
        if files:
            await interaction.response.send_message(embed=embed, files=files)
        else:
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name='tricklist', description='Show all available skateboarding tricks')
    async def tricklist(self, interaction: discord.Interaction):
        """Display a list of all skateboarding tricks"""
        basic_tricks = SKATE_TRICKS[:5]
        advanced_tricks = SKATE_TRICKS[5:20]
        grinds_slides = SKATE_TRICKS[20:]
        
        embed = discord.Embed(
            title="🛹 Complete Trick List",
            description="Here are all the tricks you can practice!",
            color=0x00ff00
        )
        
        embed.add_field(
            name="🔰 Basic Tricks",
            value="\n".join([f"• {trick}" for trick in basic_tricks]),
            inline=True
        )
        
        embed.add_field(
            name="⚡ Advanced Tricks", 
            value="\n".join([f"• {trick}" for trick in advanced_tricks]),
            inline=True
        )
        
        embed.add_field(
            name="🛹 Grinds & Slides",
            value="\n".join([f"• {trick}" for trick in grinds_slides]),
            inline=True
        )
        
        embed.set_footer(text=f"Total tricks: {len(SKATE_TRICKS)} | Use /trick to get a random one!")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='trickimages', description='Check which trick images are missing')
    @app_commands.default_permissions(manage_messages=True)
    async def trick_images(self, interaction: discord.Interaction):
        """Check which trick control images are available and which are missing"""
        
        regular_images = []
        goofy_images = []
        missing_regular = []
        missing_goofy = []
        
        for trick in SKATE_TRICKS:
            clean_trick = "".join(c for c in trick if c.isalnum() or c in (' ', '-')).rstrip()
            clean_trick = clean_trick.replace(' ', '_').lower()
            
            # Check for multiple image formats
            image_extensions = ['.png', '.jpg', '.jpeg']
            
            regular_found = False
            goofy_found = False
            
            for ext in image_extensions:
                regular_path = f"images/tricks/regular/{clean_trick}{ext}"
                goofy_path = f"images/tricks/goofy/{clean_trick}{ext}"
                
                if os.path.exists(regular_path):
                    regular_found = True
                if os.path.exists(goofy_path):
                    goofy_found = True
            
            if regular_found:
                regular_images.append(trick)
            else:
                missing_regular.append(f"{clean_trick}.png/jpg")
                
            if goofy_found:
                goofy_images.append(trick)
            else:
                missing_goofy.append(f"{clean_trick}.png/jpg")
        
        embed = discord.Embed(
            title="📸 Trick Images Status",
            description="Control sequence image availability",
            color=0x00ff00
        )
        
        embed.add_field(
            name="✅ Regular Stance Images",
            value=f"{len(regular_images)}/{len(SKATE_TRICKS)} available\n" + 
                  (", ".join(regular_images[:10]) + ("..." if len(regular_images) > 10 else "") if regular_images else "None"),
            inline=False
        )
        
        embed.add_field(
            name="✅ Goofy Stance Images", 
            value=f"{len(goofy_images)}/{len(SKATE_TRICKS)} available\n" +
                  (", ".join(goofy_images[:10]) + ("..." if len(goofy_images) > 10 else "") if goofy_images else "None"),
            inline=False
        )
        
        if missing_regular:
            embed.add_field(
                name="❌ Missing Regular Images",
                value=", ".join(missing_regular[:10]) + ("..." if len(missing_regular) > 10 else ""),
                inline=False
            )
            
        if missing_goofy:
            embed.add_field(
                name="❌ Missing Goofy Images", 
                value=", ".join(missing_goofy[:10]) + ("..." if len(missing_goofy) > 10 else ""),
                inline=False
            )
        
        embed.add_field(
            name="📁 Image Directory Structure",
            value="`images/tricks/regular/` - Regular stance screenshots\n`images/tricks/goofy/` - Goofy stance screenshots\n\n" +
                  "**File naming:** Use lowercase, underscores for spaces\n" +
                  "Example: `kickflip.png`, `tre_flip.png`",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='skatefact', description='Learn a random skateboarding fact!')
    async def skatefact(self, interaction: discord.Interaction):
        """Get a random skateboarding fact"""
        # Award points for using the command
        await self.award_trick_points(interaction.user.id)
        
        fact = random.choice(SKATE_FACTS)
        
        embed = discord.Embed(
            title="🛹 Skate Fact",
            description=fact,
            color=0x00ff00
        )
        embed.set_footer(text="The more you know! 🧠✨")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='skatehistory', description='Learn about skateboarding history')
    async def skatehistory(self, interaction: discord.Interaction):
        """Get an overview of skateboarding history"""
        embed = discord.Embed(
            title="🛹 Skateboarding History Timeline",
            color=0x00ff00
        )
        
        embed.add_field(
            name="1940s-1950s 🏄‍♂️",
            value="Surfers in California create the first skateboards by attaching roller skate wheels to wooden planks, calling it 'sidewalk surfing'.",
            inline=False
        )
        
        embed.add_field(
            name="1970s 🌊", 
            value="Urethane wheels are invented, revolutionizing skateboarding. The Z-Boys pioneer modern skateboarding style.",
            inline=False
        )
        
        embed.add_field(
            name="1978 🚀",
            value="Alan 'Ollie' Gelfand invents the ollie, the foundation of modern skateboarding tricks.",
            inline=False
        )
        
        embed.add_field(
            name="1980s-1990s 📹",
            value="Street skating develops. Skate videos become popular. Tony Hawk and others push the sport to new heights.",
            inline=False
        )
        
        embed.add_field(
            name="2020 🏅",
            value="Skateboarding makes its Olympic debut in Tokyo, cementing its place as a legitimate sport.",
            inline=False
        )
        
        embed.set_footer(text="From sidewalk surfing to Olympic sport! 🏆")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='daily', description='Check when daily missions reset (1 PM EST)')
    async def daily_reset(self, interaction: discord.Interaction):
        # Base timestamp you provided: 1728752400 = 1 PM EST on a specific day
        # We'll calculate daily resets from this base
        base_timestamp = 1728752400  # Your reference 1 PM EST timestamp
        current_timestamp = int(self.get_edt_now().timestamp())
        
        # Calculate seconds in a day
        seconds_per_day = 24 * 60 * 60
        
        # Find how many days have passed since the base timestamp
        days_since_base = (current_timestamp - base_timestamp) // seconds_per_day
        
        # Calculate today's reset time
        today_reset = base_timestamp + (days_since_base * seconds_per_day)
        
        # If we're past today's reset, use tomorrow's reset
        if current_timestamp >= today_reset:
            timestamp = today_reset + seconds_per_day
        else:
            timestamp = today_reset
        
        embed = discord.Embed(
            title="🗓️ Daily Mission Reset",
            description=f"Daily missions reset at **<t:{timestamp}:t>**\n\nTime until reset: <t:{timestamp}:R>",
            color=0x00ff88
        )
        
        embed.add_field(
            name="📅 Reset Schedule",
            value=f"Daily missions reset every day at **<t:{timestamp}:t>**\n*(Automatically adjusts to your timezone)*",
            inline=False
        )
        
        
        embed.set_footer(text="Keep grinding those daily missions! 🛹")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='weekly', description='Check when weekly missions reset (Tuesdays at 1 PM EDT)')
    async def weekly_reset(self, interaction: discord.Interaction):
        # Base timestamp: same as daily but we'll find the next Tuesday
        base_timestamp = 1728752400  # Your reference 1 PM EST timestamp
        current_timestamp = int(self.get_edt_now().timestamp())
        
        # Calculate seconds in a day and week
        seconds_per_day = 24 * 60 * 60
        seconds_per_week = 7 * seconds_per_day
        
        # Find the base date and what day of week it was
        base_date = datetime.datetime.fromtimestamp(base_timestamp)
        base_weekday = base_date.weekday()  # 0=Monday, 1=Tuesday, etc.
        
        # Calculate days since base timestamp
        days_since_base = (current_timestamp - base_timestamp) // seconds_per_day
        
        # Find the most recent Tuesday at 1 PM
        # If base was not a Tuesday, adjust to find the Tuesday pattern
        if base_weekday != 1:  # If base wasn't Tuesday
            # Find how many days to add/subtract to get to Tuesday
            days_to_tuesday = (1 - base_weekday) % 7
            tuesday_base = base_timestamp + (days_to_tuesday * seconds_per_day)
        else:
            tuesday_base = base_timestamp
        
        # Find how many weeks have passed since the Tuesday base
        weeks_since_tuesday_base = (current_timestamp - tuesday_base) // seconds_per_week
        
        # Calculate this week's Tuesday reset
        this_tuesday_reset = tuesday_base + (weeks_since_tuesday_base * seconds_per_week)
        
        # If we're past this Tuesday's reset, use next Tuesday's reset
        if current_timestamp >= this_tuesday_reset:
            timestamp = this_tuesday_reset + seconds_per_week
        else:
            timestamp = this_tuesday_reset
        
        embed = discord.Embed(
            title="📅 Weekly Mission Reset",
            description=f"Weekly missions reset at **<t:{timestamp}:t>**\n*(Automatically adjusts to your timezone)*\n\nTime until reset: <t:{timestamp}:R>",
            color=0x00ff88
        )
        
        embed.add_field(
            name="🗓️ Reset Schedule",
            value="Weekly missions reset every **Tuesday at 1:00 PM EDT**",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Pro Tip",
            value="Weekly missions give bigger rewards! Make sure to complete them before Tuesday's reset.",
            inline=False
        )
        
        embed.set_footer(text="Keep grinding those weekly missions! 🛹")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='brand', description='Learn about skateboard brand history and culture')
    async def brand(self, interaction: discord.Interaction):
        """Get information about skateboard brands - legends, history, and culture"""
        # Award points for using the command
        await self.award_trick_points(interaction.user.id)
        
        brand_data = random.choice(SKATE_BRANDS)
        
        embed = discord.Embed(
            title=f"🏢 {brand_data['name']}",
            description=brand_data['description'],
            color=0x00ff00
        )
        
        # Founded info
        embed.add_field(
            name="📅 Founded",
            value=brand_data['founded'],
            inline=True
        )
        
        # Status info
        status_emoji = "💀" if brand_data.get('defunct') else "✅"
        status_text = f"{status_emoji} {brand_data['status']}"
        embed.add_field(
            name="📊 Status",
            value=status_text,
            inline=True
        )
        
        # Location
        embed.add_field(
            name="🌍 Origin",
            value=brand_data['location'],
            inline=True
        )
        
        # Notable info or legacy
        if brand_data.get('notable'):
            embed.add_field(
                name="🌟 Notable For",
                value=brand_data['notable'],
                inline=False
            )
        
        # Fun fact
        if brand_data.get('fun_fact'):
            embed.add_field(
                name="💡 Fun Fact",
                value=brand_data['fun_fact'],
                inline=False
            )
        
        embed.set_footer(text="Respect the brands that built the culture! 🙏")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(SkateboardCommands(bot))