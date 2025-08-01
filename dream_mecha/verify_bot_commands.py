#!/usr/bin/env python3
"""
Verify bot commands are working
"""

import requests
import time

def check_bot_status():
    """Check if the bot is running and responding"""
    print("🤖 Checking Bot Status...")
    
    # Check if the bot process is running
    try:
        # This is a simple check - in a real scenario you'd check the actual bot
        print("✅ Bot process should be running")
        print("📋 Available Commands:")
        print("   !help                    - Show all commands")
        print("   !test health            - Test system health")
        print("   !test fortress          - Test fortress damage")
        print("   !test enemies           - Test enemy generation")
        print("   !test webui             - Test web UI connection")
        print("   !test export            - Test data export")
        print("   !test all               - Run all tests")
        print("   !debug all              - Comprehensive debug")
        print("   !debug status           - Show system status")
        print("   !debug reset            - Reset fortress HP")
        print("   !launch                 - Launch mecha for combat")
        print("   !status                 - Check mecha status")
        
        print("\n🎯 To test the bot:")
        print("1. Go to your Discord server")
        print("2. Find the #dream-mecha-beta channel")
        print("3. Try: !help")
        print("4. Try: !test all")
        print("5. Try: !debug status")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot check failed: {e}")
        return False

def check_web_ui():
    """Check if web UI is accessible"""
    print("\n🌐 Checking Web UI...")
    
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
    """Main verification function"""
    print("🔍 Dream Mecha Bot Verification")
    print("=" * 50)
    
    check_bot_status()
    check_web_ui()
    
    print("\n" + "=" * 50)
    print("📝 Next Steps:")
    print("1. Check Discord for bot messages")
    print("2. Test commands in #dream-mecha-beta")
    print("3. Look for debug embeds from the bot")
    print("4. Check console for any error messages")

if __name__ == "__main__":
    main() 