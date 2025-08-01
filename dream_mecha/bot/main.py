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
    
    @tasks.loop(time=datetime.time(hour=6, minute=0))
    async def daily_cycle(self):
        """Run daily game cycle at 6 AM"""
        print("🔄 Starting daily cycle at 6 AM...")
        
        # Generate new shop
        self.game_manager.shop_system.generate_daily_shop(
            voidstate=self.voidstate_manager.voidstate,
            player_count=len(self.player_manager.players)
        )
        
        # Announce daily boss
        await self.announce_daily_boss()
        
        # Check if fortress needs status update
        await self.check_fortress_status()
        
        # TEST: Trigger fortress attack for testing
        await self.test_fortress_attack()
        
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
        )
        
        # Create boss announcement embed
        embed = discord.Embed(
            title="🌌 DAILY VOID INVASION",
            description="The void has sent forth its forces!",
            color=0x8b0000  # Dark red
        )
        
        embed.add_field(
            name="Enemy Forces",
            value=f"Enemies: {len(boss_info['enemies'])}\n" +
                  f"Total Power: {sum(e.attack for e in boss_info['enemies']):,}\n" +
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
    
    # ===== COMPREHENSIVE TESTING SYSTEM =====
    
    async def send_debug_message(self, title: str, content: str, color: int = 0x00ff00):
        """Send a debug message to all guilds"""
        embed = discord.Embed(
            title=f"🔧 DEBUG: {title}",
            description=content,
            color=color,
            timestamp=datetime.now()
        )
        
        for guild in self.guilds:
            try:
                channel = discord.utils.get(guild.text_channels, name='dream-mecha-beta')
                if channel:
                    await channel.send(embed=embed)
                    print(f"✅ Debug message sent to #{channel.name}")
                    break
            except Exception as e:
                print(f"⚠️ Could not send debug message: {e}")
    
    async def test_system_health(self):
        """Test all system components"""
        try:
            # Test managers
            player_count = len(self.player_manager.players)
            fortress_status = self.fortress_manager.get_fortress_status()
            voidstate = self.voidstate_manager.voidstate
            
            # Test data persistence
            self.player_manager.save_player_data()
            self.fortress_manager.save_fortress()
            
            content = f"""
**System Health Check:**
✅ Players: {player_count}
✅ Fortress HP: {fortress_status['current_hp']:,}
✅ Voidstate: {voidstate}
✅ Data persistence: Working
✅ Bot status: Online
            """.strip()
            
            await self.send_debug_message("System Health", content, 0x00ff00)
            
        except Exception as e:
            await self.send_debug_message("System Health FAILED", f"Error: {str(e)}", 0xff0000)
    
    async def test_fortress_damage(self, damage_amount: int = 1000000):
        """Test fortress damage system"""
        try:
            # Get initial status
            initial_status = self.fortress_manager.get_fortress_status()
            
            # Apply damage
            result = self.fortress_manager.fortress.take_damage(damage_amount)
            
            # Get final status
            final_status = self.fortress_manager.get_fortress_status()
            
            content = f"""
**Fortress Damage Test:**
🔴 Initial HP: {initial_status['current_hp']:,}
⚔️ Damage Applied: {damage_amount:,}
🟢 Final HP: {final_status['current_hp']:,}
📊 HP Percentage: {final_status['hp_percentage']:.1f}%
💥 Damage Dealt: {result['damage_dealt']:,}
✅ Success: {result['success']}
            """.strip()
            
            await self.send_debug_message("Fortress Damage Test", content, 0xff6f61)
            
        except Exception as e:
            await self.send_debug_message("Fortress Damage Test FAILED", f"Error: {str(e)}", 0xff0000)
    
    async def test_enemy_generation(self):
        """Test enemy generation system"""
        try:
            # Generate test enemies
            enemies = self.game_manager.combat_system.generate_enemies(
                voidstate=self.voidstate_manager.voidstate,
                player_power=10000
            )
            
            content = f"""
**Enemy Generation Test:**
👹 Enemies Generated: {len(enemies)}
⚔️ Total Attack Power: {sum(e.attack for e in enemies):,}
🛡️ Total Defense: {sum(e.defense for e in enemies):,}
💀 Total HP: {sum(e.hp for e in enemies):,}
🌌 Voidstate: {self.voidstate_manager.voidstate}
            """.strip()
            
            await self.send_debug_message("Enemy Generation Test", content, 0x8b0000)
            
        except Exception as e:
            await self.send_debug_message("Enemy Generation Test FAILED", f"Error: {str(e)}", 0xff0000)
    
    async def test_web_ui_connection(self):
        """Test web UI connectivity"""
        try:
            import requests
            
            # Test basic connectivity
            response = requests.get(f"{self.web_ui_url}/api/status", timeout=5)
            
            if response.status_code == 200:
                content = f"""
**Web UI Connection Test:**
✅ Status: Online
🌐 URL: {self.web_ui_url}
📡 Response: {response.status_code}
⏱️ Response Time: {response.elapsed.total_seconds():.2f}s
                """.strip()
                
                await self.send_debug_message("Web UI Connection Test", content, 0x00ff00)
            else:
                await self.send_debug_message("Web UI Connection Test", f"Status code: {response.status_code}", 0xffcc00)
                
        except Exception as e:
            await self.send_debug_message("Web UI Connection Test FAILED", f"Error: {str(e)}", 0xff0000)
    
    async def test_data_export(self):
        """Test data export functionality"""
        try:
            # Export current game state
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'players': len(self.player_manager.players),
                'fortress_status': self.fortress_manager.get_fortress_status(),
                'voidstate': self.voidstate_manager.voidstate,
                'bot_guilds': len(self.guilds),
                'web_ui_url': self.web_ui_url
            }
            
            content = f"""
**Data Export Test:**
📊 Players: {export_data['players']}
🏰 Fortress HP: {export_data['fortress_status']['current_hp']:,}
🌌 Voidstate: {export_data['voidstate']}
🤖 Bot Guilds: {export_data['bot_guilds']}
🌐 Web UI: {export_data['web_ui_url']}
⏰ Timestamp: {export_data['timestamp']}
            """.strip()
            
            await self.send_debug_message("Data Export Test", content, 0x4169e1)
            
        except Exception as e:
            await self.send_debug_message("Data Export Test FAILED", f"Error: {str(e)}", 0xff0000)
    
    async def on_ready(self):
        """Called when bot is ready"""
        print(f"🤖 {self.user} is ready!")
        print(f"📊 Connected to {len(self.guilds)} guilds")
        
        # Send startup message
        if self.debug_mode:
            await self.send_debug_message("Bot Startup", "Dream Mecha Bot is online and ready!", 0x00ff00)
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        
        print(f"⚠️ Command error: {error}")
        await ctx.send(f"❌ Command error: {error}")

# ===== COMMAND SETUP =====
async def setup(bot):
    """Setup bot commands"""
    
    @bot.command(name='health')
    async def health_check(ctx):
        """Check bot health"""
        await ctx.send("✅ Bot is healthy!")
    
    @bot.command(name='help')
    async def help_command(ctx):
        """Show help information"""
        embed = discord.Embed(
            title="🤖 Dream Mecha Bot Commands",
            description="Available commands for testing and debugging",
            color=0x4169e1
        )
        
        embed.add_field(
            name="🎮 Game Commands",
            value="`!launch` - Launch your mecha for combat\n" +
                  "`!status` - Check your mecha status\n" +
                  "`!help` - Show this help message",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Debug Commands",
            value="`!test health` - Test system health\n" +
                  "`!test fortress` - Test fortress damage\n" +
                  "`!test enemies` - Test enemy generation\n" +
                  "`!test webui` - Test web UI connection\n" +
                  "`!test export` - Test data export\n" +
                  "`!debug all` - Run all debug tests",
            inline=False
        )
        
        embed.add_field(
            name="📊 Info",
            value=f"Web UI: {bot.web_ui_url}\n" +
                  f"Players: {len(bot.player_manager.players)}\n" +
                  f"Debug Mode: {bot.debug_mode}",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @bot.command(name='launch')
    async def launch_mecha(ctx):
        """Launch mecha for combat"""
        try:
            player_id = str(ctx.author.id)
            
            # Get or create player
            player = bot.player_manager.get_player(player_id)
            if not player:
                player = bot.player_manager.create_player(player_id, ctx.author.display_name)
            
            # Check if player has a mecha
            if not player.mecha:
                await ctx.send("❌ You don't have a mecha! Visit the web UI to build one.")
                return
            
            # Check if mecha is ready
            if player.mecha.state.value != 'ready':
                await ctx.send("❌ Your mecha is not ready for launch!")
                return
            
            # Launch mecha
            player.mecha.state.value = 'launched'
            bot.game_manager.combat_system.add_mecha(player.mecha)
            
            # Save player data
            bot.player_manager.save_player_data()
            
            embed = discord.Embed(
                title="🚀 MECHA LAUNCHED!",
                description=f"{ctx.author.display_name} has launched their mecha!",
                color=0x00ff00
            )
            
            embed.add_field(
                name="Mecha Stats",
                value=f"HP: {player.mecha.stats.hp:,}\n" +
                      f"Attack: {player.mecha.stats.attack:,}\n" +
                      f"Defense: {player.mecha.stats.defense:,}\n" +
                      f"Speed: {player.mecha.stats.speed:,}",
                inline=True
            )
            
            embed.add_field(
                name="Combat Status",
                value="⚔️ Ready for battle!\n" +
                      "🕐 Results at 6 AM tomorrow",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Launch failed: {e}")
    
    @bot.command(name='status')
    async def mecha_status(ctx):
        """Check mecha status"""
        try:
            player_id = str(ctx.author.id)
            player = bot.player_manager.get_player(player_id)
            
            if not player or not player.mecha:
                await ctx.send("❌ You don't have a mecha! Visit the web UI to build one.")
                return
            
            embed = discord.Embed(
                title="🤖 MECHA STATUS",
                description=f"{ctx.author.display_name}'s mecha information",
                color=0x4169e1
            )
            
            embed.add_field(
                name="Status",
                value=f"State: {player.mecha.state.value.upper()}\n" +
                      f"Zoltans: {player.zoltans:,}",
                inline=True
            )
            
            embed.add_field(
                name="Stats",
                value=f"HP: {player.mecha.stats.hp:,}\n" +
                      f"Attack: {player.mecha.stats.attack:,}\n" +
                      f"Defense: {player.mecha.stats.defense:,}\n" +
                      f"Speed: {player.mecha.stats.speed:,}",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Status check failed: {e}")
    
    # ===== DEBUG COMMANDS =====
    
    @bot.command(name='test')
    async def test_command(ctx, test_type: str = None):
        """Run various tests"""
        if not test_type:
            await ctx.send("❌ Please specify a test type: `!test health|fortress|enemies|webui|export|all`")
            return
        
        await ctx.send(f"🧪 Running {test_type} test...")
        
        if test_type == 'health':
            await bot.test_system_health()
        elif test_type == 'fortress':
            await bot.test_fortress_damage()
        elif test_type == 'enemies':
            await bot.test_enemy_generation()
        elif test_type == 'webui':
            await bot.test_web_ui_connection()
        elif test_type == 'export':
            await bot.test_data_export()
        elif test_type == 'all':
            await bot.test_system_health()
            await asyncio.sleep(1)
            await bot.test_fortress_damage()
            await asyncio.sleep(1)
            await bot.test_enemy_generation()
            await asyncio.sleep(1)
            await bot.test_web_ui_connection()
            await asyncio.sleep(1)
            await bot.test_data_export()
        else:
            await ctx.send("❌ Unknown test type. Use: `health|fortress|enemies|webui|export|all`")
    
    @bot.command(name='debug')
    async def debug_command(ctx, action: str = None):
        """Debug commands"""
        if not action:
            await ctx.send("❌ Please specify an action: `!debug all|status|reset`")
            return
        
        if action == 'all':
            await ctx.send("🔧 Running comprehensive debug...")
            await bot.test_system_health()
            await asyncio.sleep(1)
            await bot.test_fortress_damage(5000000)  # 5M damage test
            await asyncio.sleep(1)
            await bot.test_enemy_generation()
            await asyncio.sleep(1)
            await bot.test_web_ui_connection()
            await asyncio.sleep(1)
            await bot.test_data_export()
            
        elif action == 'status':
            fortress_status = bot.fortress_manager.get_fortress_status()
            content = f"""
**Current System Status:**
🤖 Bot Guilds: {len(bot.guilds)}
👥 Players: {len(bot.player_manager.players)}
🏰 Fortress HP: {fortress_status['current_hp']:,}
🌌 Voidstate: {bot.voidstate_manager.voidstate}
🌐 Web UI: {bot.web_ui_url}
🔧 Debug Mode: {bot.debug_mode}
            """.strip()
            
            await bot.send_debug_message("System Status", content, 0x4169e1)
            
        elif action == 'reset':
            # Reset fortress to full HP
            bot.fortress_manager.fortress.current_hp = bot.fortress_manager.fortress.max_hp
            bot.fortress_manager.fortress.total_damage_taken = 0
            bot.fortress_manager.fortress.days_under_attack = 0
            bot.fortress_manager.fortress.last_attack_date = None
            bot.fortress_manager.save_fortress()
            
            await bot.send_debug_message("Fortress Reset", "Fortress HP restored to maximum!", 0x00ff00)
            
        else:
            await ctx.send("❌ Unknown debug action. Use: `all|status|reset`")

def main():
    """Main function to run the bot"""
    bot = DreamMechaBot()
    
    # Setup commands
    asyncio.run(setup(bot))
    
    # Run the bot
    bot.run(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
    main() 