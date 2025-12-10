#!/usr/bin/env python
"""
Test script to verify feed.html template rendering
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_feed_template():
    """Test if feed.html template can be rendered"""
    from jinja2 import Environment, FileSystemLoader, TemplateError
    
    # Setup Jinja2 environment
    template_dir = os.path.join(os.path.dirname(__file__), 'gramatike_app', 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    
    print(f"Loading templates from: {template_dir}")
    print(f"Template directory exists: {os.path.exists(template_dir)}")
    
    # List templates
    templates = os.listdir(template_dir)
    print(f"\nAvailable templates ({len(templates)}):")
    for t in sorted(templates):
        if t.endswith('.html'):
            print(f"  - {t}")
    
    # Try to load feed.html
    print("\n" + "="*60)
    print("Testing feed.html template...")
    print("="*60)
    
    try:
        template = env.get_template('feed.html')
        print("✓ Template loaded successfully")
        
        # Read template source directly from file
        feed_path = os.path.join(template_dir, 'feed.html')
        with open(feed_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        checks = [
            ("Posts section", "#feed-list" in source or "feed-list" in source),
            ("Friends section (amigues)", "amigues" in source.lower()),
            ("Tic-tac-toe game", "jogo da velha" in source.lower() or "ttt" in source.lower()),
            ("Search functionality", "search-input" in source),
            ("Post creation", "novo_post" in source or "criar post" in source.lower()),
        ]
        
        print("\nTemplate features:")
        all_found = True
        for name, found in checks:
            status = "✓" if found else "✗"
            print(f"  {status} {name}: {'Found' if found else 'Not found'}")
            all_found &= found
        
        # Try basic render (without context - will use defaults)
        print("\nAttempting basic render...")
        try:
            # This will fail if there are required variables, but will show us the error
            html = template.render()
            print(f"✓ Template rendered successfully ({len(html)} bytes)")
        except Exception as e:
            # Expected - template needs context variables
            print(f"⚠ Template needs context variables (expected): {type(e).__name__}")
            print(f"  Message: {str(e)[:100]}")
        
        return all_found
        
    except TemplateError as e:
        print(f"✗ Template error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {type(e).__name__}: {e}")
        return False

def check_route_configuration():
    """Check if feed route is properly configured"""
    print("\n" + "="*60)
    print("Checking route configuration...")
    print("="*60)
    
    try:
        # Check if route decorator is present in source
        routes_file = os.path.join(os.path.dirname(__file__), 'gramatike_app', 'routes', '__init__.py')
        if os.path.exists(routes_file):
            with open(routes_file, 'r') as f:
                content = f.read()
                
            has_feed_route = "@bp.route('/feed')" in content
            has_login_required = "@login_required" in content
            
            # Check if @login_required comes before def feed()
            try:
                feed_route_index = content.index("@bp.route('/feed')")
                feed_def_index = content.index("def feed():")
                login_req_lines = content[feed_route_index:feed_def_index]
                has_login_decorator = "@login_required" in login_req_lines
            except ValueError:
                has_login_decorator = False
            
            print(f"\n✓ Routes file found: {routes_file}")
            print(f"  {'✓' if has_feed_route else '✗'} /feed route defined")
            print(f"  {'✓' if has_login_decorator else '✗'} @login_required decorator present for feed route")
            
            # Find feed function
            if 'def feed():' in content:
                # Extract feed function
                start = content.index('def feed():')
                # Find next function or end
                next_def = content.find('\n@bp.route', start + 1)
                if next_def == -1:
                    next_def = content.find('\ndef ', start + 20)
                
                feed_func = content[start:next_def if next_def != -1 else start+500]
                
                print(f"\n  Feed function preview:")
                for line in feed_func.split('\n')[:15]:
                    print(f"    {line}")
                
                # Check what template is being rendered
                if "render_template('feed.html')" in feed_func:
                    print("\n  ✓ Function renders feed.html template")
                else:
                    print("\n  ✗ Function does NOT render feed.html template")
                
                return has_feed_route and has_login_decorator
        else:
            print(f"✗ Routes file not found: {routes_file}")
            return False
            
    except Exception as e:
        print(f"✗ Error checking routes: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("FEED TEMPLATE TEST")
    print("=" * 60)
    
    success = True
    success &= test_feed_template()
    success &= check_route_configuration()
    
    print("\n" + "="*60)
    if success:
        print("✓ All checks passed!")
        print("\nFeed template has all required features:")
        print("  - Posts feed (#feed-list)")
        print("  - Friends sidebar (amigues)")
        print("  - Tic-tac-toe game (jogo da velha)")
    else:
        print("✗ Some checks failed - see details above")
    print("="*60)
    
    sys.exit(0 if success else 1)
