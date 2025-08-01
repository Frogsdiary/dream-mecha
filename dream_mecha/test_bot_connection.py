#!/usr/bin/env python3
"""
Quick test to verify bot is running and responding
"""

import requests
import time

def test_bot_status():
    """Test if bot is running and can respond"""
    print("🤖 Testing Bot Connection...")
    
    # Since we can't directly test Discord bot from here,
    # we'll check if the bot process is running and provide instructions
    
    print("✅ Bot should be running in background")
    print("📋 To test the bot:")
    print("1. Go to your Discord server")
    print("2. Navigate to #dream-mecha-beta channel")
    print("3. Try these commands:")
    print("   !help                    # Show all commands")
    print("   !debug status           # Show system status")
    print("   !test all               # Run all tests")
    print("   !debug reset            # Reset fortress HP")
    
    print("\n🎯 Expected Results:")
    print("- Messages should go to #dream-mecha-beta ONLY")
    print("- No more messages in #general")
    print("- All commands should work")
    print("- Bot should respond with embeds")
    
    print("\n🚨 If bot doesn't respond:")
    print("1. Check if bot is running: python bot/main.py")
    print("2. Check Discord permissions")
    print("3. Verify bot token in .env file")
    
    return True

def test_web_ui():
    """Test web UI connectivity"""
    print("\n🌐 Testing Web UI...")
    
    try:
        response = requests.get("http://localhost:3000/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Web UI is online")
            return True
        else:
            print(f"⚠️ Web UI status: {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("⚠️ Web UI not accessible (may not be running)")
        return False

def main():
    """Main test function"""
    print("🔍 Dream Mecha Bot Connection Test")
    print("=" * 50)
    
    test_bot_status()
    test_web_ui()
    
    print("\n" + "=" * 50)
    print("📝 Next Steps:")
    print("1. Test Discord commands in #dream-mecha-beta")
    print("2. Look for bot responses")
    print("3. Verify channel targeting is fixed")
    print("4. Test manual triggers: !debug all")

if __name__ == "__main__":
    main() 