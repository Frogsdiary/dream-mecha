"""
Main Discord bot for Dream Mecha game
Handles daily cycles, announcements, and web UI integration
"""

import os
import sys
import asyncio
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime
import json

# Add the parent directory to the path so we can import core modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.managers.game_manager import GameManager
from core.managers.player_manager import PlayerManager
from core.managers.voidstate_manager import VoidstateManager

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
        self.fortress_manager = self.game_manager.fortress_manager
        
        # Web UI URL (will be set from Railway environment)
        self.web_ui_url = os.getenv('WEB_UI_URL', 'http://localhost:3000')
        
        # Debug mode flag
        self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        
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
    
    @tasks.loop(minutes=1)
    async def daily_cycle(self):
        """Run daily game cycle at 6 AM"""
        # Check if it's 6 AM
        now = datetime.now()
        if now.hour != 6 or now.minute != 0:
            return
            
        print("🔄 Starting daily cycle at 6 AM...")
        
        # Generate new shop
        self.game_manager.shop_system.generate_daily_shop(
            voidstate=self.voidstate_manager.voidstate,
            player_count=len(self.player_manager.players)
        )
        
        # DISABLED: Discord announcements temporarily disabled
        # await self.announce_daily_boss()
        
        # Resolve combat if mechas are launched
        if self.game_manager.combat_system.launched_mechas:
            print("⚔️ Resolving combat...")
            combat_result = self.game_manager.resolve_combat()
            # await self.announce_combat_results(combat_result)
        
        # Check if fortress needs status update
        # await self.check_fortress_status()
        
        # TEST: Trigger fortress attack for testing
        # await self.test_fortress_attack()
        
        # Reset player launch status
        for player in self.player_manager.players.values():
            if player.mecha:
                player.mecha.state = player.mecha.state.READY
        
        print("✅ Daily cycle completed")
    
    async def announce_combat_results(self, combat_result):
        """Announce combat results to all guilds"""
        print("📢 Announcing combat results...")
        
        # Determine embed color based on result
        if combat_result['enemies_remaining'] == 0:
            color = 0x00ff00  # Green for victory
            title = "🎉 VICTORY! Void Forces Defeated"
        else:
            color = 0xff0000  # Red for defeat
            title = "💀 DEFEAT! Void Forces Remain"
        
        embed = discord.Embed(
            title=title,
            description="Battle against the void has concluded!",
            color=color
        )
        
        # Combat statistics
        mechas_launched = len(combat_result.get('mechas_launched', []))
        mechas_downed = combat_result.get('mechas_downed', 0)
        enemies_defeated = combat_result.get('enemies_defeated', 0)
        total_enemies = combat_result.get('total_enemies', 0)
        
        embed.add_field(
            name="⚔️ Combat Statistics",
            value=f"Mechas Launched: {mechas_launched}\n" +
                  f"Mechas Downed: {mechas_downed}\n" +
                  f"Enemies Defeated: {enemies_defeated}/{total_enemies}\n" +
                  f"Enemies Remaining: {combat_result['enemies_remaining']}",
            inline=True
        )
        
        # Zoltan rewards
        zoltan_rewards = combat_result.get('zoltan_rewards', {})
        if zoltan_rewards:
            reward_text = ""
            for player_id, reward in zoltan_rewards.items():
                player_name = self.player_manager.players.get(player_id, {}).get('name', f"Player {player_id}")
                reward_text += f"{player_name}: {reward} Zoltan\n"
            
            embed.add_field(
                name="💰 Zoltan Rewards",
                value=reward_text or "No rewards distributed",
                inline=True
            )
        
        # Voidstate changes
        voidstate_change = combat_result.get('voidstate_change', 0)
        embed.add_field(
            name="🌌 Voidstate",
            value=f"New Level: {voidstate_change}\n" +
                  f"Change: {'+' if voidstate_change > self.voidstate_manager.voidstate else ''}{voidstate_change - self.voidstate_manager.voidstate}",
            inline=True
        )
        
        # Combat log highlights (last 3 entries)
        combat_log = combat_result.get('combat_log', [])
        if combat_log:
            log_highlights = "\n".join(combat_log[-3:])  # Last 3 entries
            embed.add_field(
                name="📜 Combat Log",
                value=log_highlights,
                inline=False
            )
        
        # Send to all guilds
        for guild in self.guilds:
            try:
                # Find a suitable channel (ONLY dream-mecha-beta)
                channel = None
                for channel_name in ['dream-mecha-beta']:
                    channel = discord.utils.get(guild.text_channels, name=channel_name)
                    if channel:
                        break
                
                if channel:
                    await channel.send(embed=embed)
                    print(f"✅ Combat results sent to #{channel.name} in {guild.name}")
                    
            except Exception as e:
                print(f"⚠️ Could not send combat results to {guild.name}: {e}")
    
    async def announce_daily_boss(self):
        """Announce the daily boss to all guilds"""
        # Calculate total player power for enemy scaling
        total_power = sum(
            player.mecha.stats.hp + player.mecha.stats.attack + player.mecha.stats.defense 
            for player in self.player_manager.players.values() 
            if player.mecha
        ) if self.player_manager.players else 1000
        
        enemies = self.game_manager.combat_system.generate_enemies(
            voidstate=self.voidstate_manager.voidstate,
            player_power=total_power
        )
        
        # Create boss announcement embed
        embed = discord.Embed(
            title="🌌 DAILY VOID INVASION",
            description="The void has sent forth its forces!",
            color=0x8b0000  # Dark red
        )
        
        embed.add_field(
            name="Enemy Forces",
            value=f"Enemies: {len(enemies)}\n" +
                  f"Total Power: {sum(e.attack for e in enemies):,}\n" +
                  f"Voidstate: {self.voidstate_manager.voidstate}",
            inline=True
        )
        
        embed.add_field(
            name="Call to Action",
            value=f"🔗 [Launch Your Mecha]({self.web_ui_url})\n" +
                  "⚔️ Use `!launch` to defend humanity!",
            inline=True
        )
        
        # Send to all guilds
        for guild in self.guilds:
            try:
                # Find a suitable channel (ONLY dream-mecha-beta)
                channel = None
                for channel_name in ['dream-mecha-beta']:
                    channel = discord.utils.get(guild.text_channels, name=channel_name)
                    if channel:
                        break
                
                if channel:
                    await channel.send(embed=embed)
                    print(f"✅ Daily boss announcement sent to #{channel.name} in {guild.name}")
                    
            except Exception as e:
                print(f"⚠️ Could not send announcement to {guild.name}: {e}")
    
    async def check_fortress_status(self):
        """Check and announce fortress status if under attack"""
        fortress_status = self.fortress_manager.get_fortress_status()
        
        # Only announce if fortress has taken damage or is under attack
        if fortress_status['days_under_attack'] > 0 or fortress_status['total_damage_taken'] > 0:
            await self.announce_fortress_status(fortress_status)
    
    async def announce_fortress_status(self, fortress_status):
        """Announce fortress status to all guilds"""
        hp_percent = fortress_status['hp_percentage']
        
        # Create status embed based on fortress condition
        if fortress_status['current_hp'] <= 0:
            embed = discord.Embed(
                title="💀 FORTRESS HAS FALLEN!",
                description="The Tower has been destroyed...",
                color=0xff0000  # Red
            )
        elif hp_percent < 50:
            embed = discord.Embed(
                title="🚨 FORTRESS UNDER CRITICAL ATTACK!",
                description="The void forces are overwhelming our defenses!",
                color=0xff6f61  # Orange-red
            )
        elif hp_percent < 80:
            embed = discord.Embed(
                title="⚠️ FORTRESS UNDER ATTACK",
                description="Void enemies are attacking the fortress directly!",
                color=0xffcc00  # Yellow
            )
        else:
            return  # Don't announce if fortress is mostly healthy
        
        embed.add_field(
            name="Fortress Status",
            value=f"HP: {fortress_status['current_hp']:,} / {fortress_status['max_hp']:,}\n" +
                  f"Health: {hp_percent:.1f}%\n" +
                  f"Days Under Attack: {fortress_status['days_under_attack']}",
            inline=True
        )
        
        embed.add_field(
            name="Call to Action",
            value=f"🔗 [Launch Your Mecha]({self.web_ui_url})\n" +
                  "⚔️ Use `!launch` to defend humanity!",
            inline=True
        )
        
        # Send to all guilds
        for guild in self.guilds:
            try:
                # Find dream-mecha-beta channel
                channel = None
                for channel_name in ['dream-mecha-beta']:
                    channel = discord.utils.get(guild.text_channels, name=channel_name)
                    if channel:
                        break
                
                if channel:
                    await channel.send(embed=embed)
                    print(f"✅ Fortress status sent to #{channel.name} in {guild.name}")
                    
            except Exception as e:
                print(f"⚠️ Could not send fortress status to {guild.name}: {e}")
    
    async def test_fortress_attack(self):
        """TEST: Manually trigger fortress attack for testing"""
        try:
            # Simulate enemy attack on fortress
            enemy_power = 50000  # Test enemy power
            fortress_result = self.fortress_manager.fortress_under_attack(
                enemy_power=enemy_power,
                no_mechs_launched=True
            )
            
            if fortress_result['attack_occurred']:
                print(f"🧪 TEST: Fortress attacked! Damage: {fortress_result['fortress_damage']:,}")
                
                # Send test announcement
                for guild in self.guilds:
                    try:
                        channel = discord.utils.get(guild.text_channels, name='dream-mecha-beta')
                        if channel:
                            embed = discord.Embed(
                                title="🧪 TEST: Fortress Attack Triggered",
                                description="This is a test of the fortress damage system",
                                color=0xff6f61
                            )
                            embed.add_field(
                                name="Test Results",
                                value=f"Enemy Power: {enemy_power:,}\n" +
                                      f"Fortress Damage: {fortress_result['fortress_damage']:,}\n" +
                                      f"Message: {fortress_result['message']}",
                                inline=False
                            )
                            await channel.send(embed=embed)
                            print(f"✅ Test fortress attack sent to #{channel.name}")
                            break  # Only send to first guild
                    except Exception as e:
                        print(f"⚠️ Could not send test fortress attack: {e}")
                        
        except Exception as e:
            print(f"⚠️ Test fortress attack failed: {e}")
    
    # ===== MINIMAL BOT FUNCTIONALITY =====
    
    async def send_announcement(self, title: str, content: str, color: int = 0x00ff00):
        """Send an announcement to all guilds"""
        embed = discord.Embed(
            title=title,
            description=content,
            color=color,
            timestamp=datetime.now()
        )
        
        for guild in self.guilds:
            try:
                channel = discord.utils.get(guild.text_channels, name='dream-mecha-beta')
                if channel:
                    await channel.send(embed=embed)
                    print(f"✅ Announcement sent to #{channel.name}")
                    break
            except Exception as e:
                print(f"⚠️ Could not send announcement: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        print(f"🤖 {self.user} is ready!")
        print(f"📊 Connected to {len(self.guilds)} guilds")
        
        # Send startup message
        if self.debug_mode:
            print("🤖 Bot Online - Dream Mecha Bot is online and ready!")
            # await self.send_announcement("🤖 Bot Online", "Dream Mecha Bot is online and ready!", 0x00ff00)
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        print(f"⚠️ Command error: {error}")
        await ctx.send(f"❌ Command error: {error}")

# ===== COMMAND SETUP =====
async def setup(bot):
    """Setup bot commands"""
    
    @bot.command(name='connect')
    async def connect_command(ctx):
        """Connect to the Dream Mecha web UI"""
        embed = discord.Embed(
            title="🌐 Dream Mecha Web UI",
            description="Click the link below to access the full game interface!",
            color=0x4169e1,
            url=bot.web_ui_url
        )
        
        embed.add_field(
            name="🎮 What you can do:",
            value="• Build and customize your mecha\n" +
                  "• Browse the daily shop\n" +
                  "• View your piece library\n" +
                  "• Check combat logs\n" +
                  "• Launch for battle",
            inline=False
        )
        
        embed.add_field(
            name="⚔️ Game Status",
            value=f"Players: {len(bot.player_manager.players)}\n" +
                  f"Fortress HP: {bot.fortress_manager.get_fortress_status()['current_hp']:,}\n" +
                  f"Voidstate: {bot.voidstate_manager.voidstate}",
            inline=True
        )
        
        embed.add_field(
            name="🔗 Quick Access",
            value=f"[Open Web UI]({bot.web_ui_url})",
            inline=True
        )
        
        await ctx.send(embed=embed)

def main():
    """Main function to run the bot"""
    # Debug environment variables with more detail
    token = os.getenv('DISCORD_TOKEN')
    web_url = os.getenv('WEB_UI_URL')
    debug_mode = os.getenv('DEBUG_MODE')
    
    print(f"🔍 Environment Check:")
    print(f"   DISCORD_TOKEN: {'SET' if token else 'MISSING'}")
    print(f"   WEB_UI_URL: {web_url if web_url else 'NOT SET'}")
    print(f"   DEBUG_MODE: {debug_mode if debug_mode else 'NOT SET'}")
    
    # List all environment variables for debugging
    print(f"🔍 All Environment Variables:")
    for key, value in os.environ.items():
        if 'DISCORD' in key or 'WEB' in key or 'FLASK' in key:
            print(f"   {key}: {'SET' if value else 'MISSING'}")
    
    if not token:
        print("❌ ERROR: DISCORD_TOKEN is not set!")
        print("   Please check Railway environment variables")
        print("   Make sure the variable name is exactly 'DISCORD_TOKEN'")
        return
    
    print(f"✅ Token found, starting bot...")
    
    bot = DreamMechaBot()
    
    # Setup commands
    asyncio.run(setup(bot))
    
    # Run the bot
    bot.run(token)

if __name__ == '__main__':
    main() 