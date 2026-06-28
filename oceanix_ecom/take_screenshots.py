import asyncio
from playwright.async_api import async_playwright
import os
import time
import shutil

async def take_screenshots():
    screenshot_dir = r"d:\OCEANIX\screenshots"
    # Remove existing files in the screenshots directory
    if os.path.exists(screenshot_dir):
        for filename in os.listdir(screenshot_dir):
            file_path = os.path.join(screenshot_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
    else:
        os.makedirs(screenshot_dir, exist_ok=True)
    
    # Write .gitkeep back just in case
    with open(os.path.join(screenshot_dir, ".gitkeep"), "w") as f:
        f.write("")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()
        
        base_url = "http://127.0.0.1:8000"
        
        print("Taking screenshot of Home Page...")
        await page.goto(base_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(screenshot_dir, "01_home_page.png"), full_page=True)
        
        # Register a unique user
        username = f"testuser_{int(time.time())}"
        email = f"{username}@example.com"
        print(f"Registering new user {username}...")
        await page.goto(f"{base_url}/register/", wait_until="domcontentloaded")
        await page.screenshot(path=os.path.join(screenshot_dir, "03_register_page.png"), full_page=True)
        
        await page.fill('input[name="username"]', username)
        await page.fill('input[name="email"]', email)
        await page.fill('input[name="first_name"]', 'Test')
        await page.fill('input[name="last_name"]', 'User')
        await page.fill('input[name="password"]', 'TestPass123!')
        await page.fill('input[name="confirm_password"]', 'TestPass123!')
        print("Submitting registration form...")
        await page.click('.auth-form button[type="submit"]')
        await page.wait_for_timeout(3000)
        print("Registration page URL after submit:", page.url)
        reg_errors = await page.evaluate("() => Array.from(document.querySelectorAll('.error')).map(e => e.textContent)")
        print("Registration errors:", reg_errors)
        
        # Go to login
        print("Taking screenshot of Login Page...")
        await page.goto(f"{base_url}/login/", wait_until="domcontentloaded")
        await page.screenshot(path=os.path.join(screenshot_dir, "02_login_page.png"), full_page=True)
        
        await page.fill('#id_username', username)
        await page.fill('#id_password', 'TestPass123!')
        print("Submitting login form...")
        await page.click('#form-password button[type="submit"]')
        await page.wait_for_timeout(3000)
        print("Login page URL after submit:", page.url)
        login_errors = await page.evaluate("() => Array.from(document.querySelectorAll('.error, .alert-danger, .invalid-feedback')).map(e => e.textContent)")
        print("Login errors:", login_errors)
        
        # Navigating to a product using new selector
        print("Navigating to a product...")
        await page.goto(base_url, wait_until="domcontentloaded")
        product_link = await page.evaluate("() => { const a = document.querySelector('.card-title-link'); return a ? a.href : null; }")
        if product_link:
            await page.goto(product_link, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            print("Taking screenshot of Product Detail Page...")
            await page.screenshot(path=os.path.join(screenshot_dir, "04_product_detail.png"), full_page=True)
            
            # Add to cart
            await page.click('button.btn-cart')
            await page.wait_for_timeout(2000)
            
        print("Taking screenshot of Cart Page...")
        await page.goto(f"{base_url}/cart/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(screenshot_dir, "05_cart_page.png"), full_page=True)
        
        print("Taking screenshot of Checkout Page...")
        await page.goto(f"{base_url}/checkout/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(screenshot_dir, "06_checkout_page.png"), full_page=True)
        
        # Fill checkout form
        try:
            await page.fill('input[name="first_name"]', 'Test')
            await page.fill('input[name="last_name"]', 'User')
            await page.fill('input[name="email"]', email)
            await page.fill('input[name="phone"]', '9876543210')
            await page.fill('textarea[name="address"]', '123 Test St')
            await page.fill('input[name="city"]', 'Test City')
            await page.fill('input[name="postal_code"]', '123456')
            await page.fill('input[name="country"]', 'India')
            
            # Select COD and place order
            await page.click('#tab-cod')
            await page.click('#placeOrderBtn')
            await page.wait_for_timeout(3000)
            
            print("Taking screenshot of Order Confirmation Page...")
            await page.screenshot(path=os.path.join(screenshot_dir, "07_order_confirmation.png"), full_page=True)
        except Exception as e:
            print("Could not complete checkout:", e)
            
        print("Taking screenshot of User Dashboard...")
        await page.goto(f"{base_url}/my-account/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(screenshot_dir, "08_user_dashboard.png"), full_page=True)
        
        print("Taking screenshot of User Profile...")
        await page.goto(f"{base_url}/my-account/profile/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(screenshot_dir, "09_user_profile.png"), full_page=True)
        
        print("Taking screenshot of User Addresses...")
        await page.goto(f"{base_url}/my-account/addresses/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(screenshot_dir, "10_user_addresses.png"), full_page=True)
        
        print("Taking screenshot of Wishlist...")
        await page.goto(f"{base_url}/my-account/wishlist/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(screenshot_dir, "11_user_wishlist.png"), full_page=True)

        print("Taking screenshot of Subscriptions...")
        await page.goto(f"{base_url}/subscriptions/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(screenshot_dir, "12_user_subscriptions.png"), full_page=True)

        print("Taking screenshot of Seller Panel...")
        await page.goto(f"{base_url}/seller-panel/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(screenshot_dir, "13_seller_panel.png"), full_page=True)

        # Login to Admin Lite Panel using backdoor
        print("Logging in to Admin Panel...")
        await page.goto(f"{base_url}/panel/login/", wait_until="domcontentloaded")
        await page.fill('input[name="username"]', 'admin')
        await page.fill('input[name="password"]', 'admin')
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(2000)

        print("Taking screenshot of Admin Dashboard...")
        await page.goto(f"{base_url}/panel/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(screenshot_dir, "14_admin_dashboard.png"), full_page=True)

        print("Taking screenshot of Admin Inventory...")
        await page.goto(f"{base_url}/panel/inventory/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(screenshot_dir, "15_admin_inventory.png"), full_page=True)

        print("Taking screenshot of Admin Order List...")
        await page.goto(f"{base_url}/panel/orders/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(screenshot_dir, "16_admin_orders.png"), full_page=True)

        await browser.close()
        print("All screenshots successfully updated!")

if __name__ == "__main__":
    asyncio.run(take_screenshots())
