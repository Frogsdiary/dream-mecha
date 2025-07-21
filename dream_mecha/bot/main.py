"""
Main Discord bot for Dream Mecha game
Handles daily cycles, announcements, and web UI integration
"""

import os
import asyncio
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from ..core.managers.game_manager import GameManager
from ..core.managers.player_manager import PlayerManager
from ..core.managers.voidstate_manager import VoidstateManager

# Load environment variables
load_dotenv()

class DreamMechaBot(commands.Bot):
    """Main Discord bot for Dream Mecha game"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        # Initialize game managers
        self.game_manager = GameManager()
        self.player_manager = PlayerManager()
        self.voidstate_manager = VoidstateManager()
        
        # Web UI URL (will be set from Railway environment)
        self.web_ui_url = os.getenv('WEB_UI_URL', 'http://localhost:3000')
        
    async def setup_hook(self):
        """Setup bot when it starts"""
        print("🤖 Dream Mecha Bot starting up...")
        
        # Load game data
        await self.load_game_data()
        
        # Start daily cycle task
        self.daily_cycle.start()
        
    async def load_game_data(self):
        """Load existing game data"""
        try:
            # Player data is loaded automatically in __init__
            print(f"📊 Loaded {len(self.player_manager.players)} players")
            
            # Load game state
            print("🎮 Game data loaded successfully")
        except Exception as e:
            print(f"⚠️ Error loading game data: {e}")
    
    @tasks.loop(hours=24)
    async def daily_cycle(self):
        """Run daily game cycle"""
        print("🔄 Starting daily cycle...")
        
        # Generate new shop
        self.game_manager.shop_system.generate_daily_shop()
        
        # Announce daily boss
        await self.announce_daily_boss()
        
        # Reset player launch status
        for player in self.player_manager.players.values():
            if player.mecha:
                player.mecha.state = player.mecha.state.READY
        
        print("✅ Daily cycle completed")
    
    async def announce_daily_boss(self):
        """Announce the daily boss to all guilds"""
        # Calculate total player power for enemy scaling
        total_power = sum(
            player.mecha.stats.hp + player.mecha.stats.attack + player.mecha.stats.defense 
            for player in self.player_manager.players.values() 
            if player.mecha
        ) if self.player_manager.players else 1000
        
        boss_info = self.game_manager.combat_system.generate_enemies(
            voidstate=self.voidstate_manager.voidstate,
            player_power=total_power
        )[0]
        
        embed = discord.Embed(
            title="🌌 Daily Void Boss Spawned!",
            description=f"A {boss_info.name} has emerged from the void!",
            color=0xff6f61
        )
        
        embed.add_field(
            name="Boss Stats",
            value=f"HP: {boss_info.hp:,}\nAttack: {boss_info.attack:,}\nDefense: {boss_info.defense:,}",
            inline=True
        )
        
        embed.add_field(
            name="Actions",
            value=f"🔗 [Manage Your Mecha]({self.web_ui_url})\n⚔️ Use `!launch` to join combat",
            inline=True
        )
        
        # Send to all guilds the bot is in
        for guild in self.guilds:
            try:
                # Find a suitable channel (general, announcements, or first text channel)
                channel = None
                for channel_name in ['general', 'announcements', 'dream-mecha']:
                    channel = discord.utils.get(guild.text_channels, name=channel_name)
                    if channel:
                        break
                
                if not channel and guild.text_channels:
                    channel = guild.text_channels[0]
                
                if channel:
                    await channel.send(embed=embed)
                    
            except Exception as e:
                print(f"⚠️ Could not send announcement to {guild.name}: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        print(f"🤖 {self.user} is online!")
        print(f"🌐 Web UI URL: {self.web_ui_url}")
        
        # Set bot status
        await self.change_presence(
            activity=discord.Game(name="Dream Mecha | !help")
        )
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        else:
            await ctx.send(f"❌ An error occurred: {error}")

# Bot commands
async def setup(bot):
    """Setup bot commands"""
    
    @bot.command(name='help')
    async def help_command(ctx):
        """Show help information"""
        embed = discord.Embed(
            title="🤖 Dream Mecha Bot Commands",
            description="Commands to interact with the Dream Mecha game",
            color=0xf7c873
        )
        
        embed.add_field(
            name="🎮 Game Commands",
            value="`!launch` - Launch your mecha for combat\n"
                  "`!status` - Check your mecha status\n"
                  "`!shop` - View daily shop\n"
                  "`!grid` - Open grid management",
            inline=False
        )
        
        embed.add_field(
            name="📊 Info Commands",
            value="`!stats` - View server statistics\n"
                  "`!leaderboard` - View top players\n"
                  "`!voidstate` - Check current voidstate",
            inline=False
        )
        
        embed.add_field(
            name="🔗 Quick Links",
            value=f"[Grid Manager]({bot.web_ui_url})\n"
                  "[Game Rules]({bot.web_ui_url}/rules)",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @bot.command(name='launch')
    async def launch_mecha(ctx):
        """Launch player's mecha for combat"""
        player_id = str(ctx.author.id)
        
        # Get or create player
        player = bot.player_manager.get_player(player_id)
        if not player:
            player = bot.player_manager.create_player(player_id, ctx.author.display_name)
        
        # Check if player has a mecha
        if not player.mechas:
            await ctx.send("❌ You don't have a mecha yet! Use the grid manager to build one.")
            return
        
        # Launch mecha
        mecha = player.mechas[0]  # Use first mecha for now
        if mecha.state != mecha.state.READY:
            await ctx.send(f"❌ Your mecha is {mecha.state.name.lower()} and cannot launch.")
            return
        
        if mecha.stats.hp < mecha.stats.max_hp * 0.5:
            await ctx.send("❌ Your mecha needs at least 50% HP to launch.")
            return
        
        # Launch the mecha
        bot.game_manager.launch_mecha(player_id, mecha.id)
        
        embed = discord.Embed(
            title="🚀 Mecha Launched!",
            description=f"{ctx.author.display_name} has launched their mecha!",
            color=0x7ed957
        )
        
        embed.add_field(
            name="Mecha Stats",
            value=f"HP: {mecha.stats.hp:,}/{mecha.stats.max_hp:,}\n"
                  f"Attack: {mecha.stats.attack:,}\n"
                  f"Defense: {mecha.stats.defense:,}\n"
                  f"Speed: {mecha.stats.speed:,}",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @bot.command(name='status')
    async def mecha_status(ctx):
        """Show player's mecha status"""
        player_id = str(ctx.author.id)
        player = bot.player_manager.get_player(player_id)
        
        if not player or not player.mechas:
            await ctx.send("❌ You don't have a mecha yet! Use the grid manager to build one.")
            return
        
        mecha = player.mechas[0]
        
        embed = discord.Embed(
            title=f"🤖 {ctx.author.display_name}'s Mecha",
            color=0xf7c873
        )
        
        embed.add_field(
            name="Status",
            value=f"State: {mecha.state.name}\n"
                  f"HP: {mecha.stats.hp:,}/{mecha.stats.max_hp:,}\n"
                  f"Zoltans: {player.zoltans:,}",
            inline=True
        )
        
        embed.add_field(
            name="Stats",
            value=f"Attack: {mecha.stats.attack:,}\n"
                  f"Defense: {mecha.stats.defense:,}\n"
                  f"Speed: {mecha.stats.speed:,}",
            inline=True
        )
        
        await ctx.send(embed=embed)

def main():
    """Main function to run the bot"""
    bot = DreamMechaBot()
    
    # Get bot token from environment
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("❌ DISCORD_BOT_TOKEN not found in environment variables!")
        return
    
    # Run the bot
    bot.run(token)

if __name__ == "__main__":
    main() 