from flask import Flask, render_template_string, jsonify, request
import json
from datetime import datetime
import os
from flask import Flask, render_template, request, redirect
from pymongo import MongoClient

app = Flask(__name__)

# ========== قاعدة البيانات البسيطة ==========
DB = {
    "products": [
        {
            "id": 1,
            "name": "هاتف سامسونج جالاكسي S22",
            "price": 2999,
            "image": "https://images.samsung.com/is/image/samsung/p6pim/ar/2202/gallery/ar-galaxy-s22-s901-412360-sm-s901ezkgmid-531166834",
            "category": "إلكترونيات",
            "rating": 4.5,
            "is_featured": True
        },
        {
            "id": 2,
            "name": "حاسوب ديل XPS 15",
            "price": 5999,
            "image": "https://i.dell.com/is/image/DellContent/content/dam/ss2/product-images/dell-client-products/notebooks/xps-notebooks/xps-15-9520/media-gallery/notebook-xps-9520-t-black-gallery-1.psd?fmt=png-alpha&pscan=auto&scl=1&hei=402&wid=536&qlt=100,0&resMode=sharp2&size=536,402",
            "category": "إلكترونيات",
            "rating": 4.8,
            "is_featured": True
        },
        {
            "id": 3,
            "name": "ساعة أبل الذكية",
            "price": 1899,
            "image": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/MKUQ3_VW_34FR+watch-40-alum-midnight-nc-7s_VW_34FR_WF_CO?wid=750&hei=712&trim=1,0&fmt=p-jpg&qlt=95&.v=1632171038000,1631661870000",
            "category": "إلكترونيات",
            "rating": 4.7,
            "is_featured": False
        }
    ],
    "categories": [
        {"id": 1, "name": "إلكترونيات", "parent_id": None},
        {"id": 2, "name": "أزياء", "parent_id": None},
        {"id": 3, "name": "هواتف ذكية", "parent_id": 1},
        {"id": 4, "name": "ملابس رجالية", "parent_id": 2}
    ],
    "users": [],
    "orders": [],
    "sessions": {}
}

# ========== واجهة الموقع ==========
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zent Shop - المتجر الإلكتروني الرائد</title>
    <style>
        /* نظام الألوان */
        :root {
            --primary: #4361ee;
            --primary-dark: #3a56d4;
            --secondary: #3f37c9;
            --accent: #4895ef;
            --light: #f8f9fa;
            --dark: #212529;
            --success: #4cc9f0;
            --warning: #f72585;
            --gray: #6c757d;
            --light-gray: #e9ecef;
        }
        
        /* التنسيقات العامة */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Tajawal', sans-serif;
            line-height: 1.6;
            color: var(--dark);
            background-color: var(--light);
        }
        
        a {
            text-decoration: none;
            color: inherit;
        }
        
        ul {
            list-style: none;
        }
        
        .container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 15px;
        }
        
        /* التنسيقات الخاصة بالهيدر */
        .header {
            background-color: var(--primary);
            color: white;
            padding: 15px 0;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header .container {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: 700;
            color: white;
        }
        
        .search-bar {
            flex: 1;
            margin: 0 20px;
            position: relative;
        }
        
        .search-bar form {
            display: flex;
        }
        
        .search-bar input {
            width: 100%;
            padding: 10px 15px;
            border: none;
            border-radius: 30px 0 0 30px;
            font-size: 1rem;
        }
        
        .search-bar button {
            background-color: var(--secondary);
            color: white;
            border: none;
            padding: 0 20px;
            border-radius: 0 30px 30px 0;
            cursor: pointer;
        }
        
        .user-menu {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .user-menu a {
            display: flex;
            flex-direction: column;
            align-items: center;
            font-size: 0.9rem;
        }
        
        .user-menu i {
            font-size: 1.2rem;
            margin-bottom: 3px;
        }
        
        .cart-count {
            background-color: var(--warning);
            color: white;
            border-radius: 50%;
            padding: 2px 6px;
            font-size: 0.7rem;
            position: absolute;
            top: -5px;
            right: -5px;
        }
        
        /* القائمة المتنقلة */
        .mobile-menu-toggle {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            display: none;
            cursor: pointer;
        }
        
        /* القائمة الجانبية */
        .sidebar {
            width: 250px;
            background-color: white;
            position: fixed;
            top: 0;
            right: -250px;
            height: 100vh;
            z-index: 1001;
            transition: right 0.3s ease;
            box-shadow: -2px 0 10px rgba(0,0,0,0.1);
        }
        
        .sidebar.active {
            right: 0;
        }
        
        /* بطاقة المنتج */
        .product-card {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.3s;
            margin-bottom: 20px;
        }
        
        .product-card:hover {
            transform: translateY(-5px);
        }
        
        .product-image {
            height: 200px;
            overflow: hidden;
        }
        
        .product-image img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s;
        }
        
        .product-card:hover .product-image img {
            transform: scale(1.05);
        }
        
        .product-info {
            padding: 15px;
        }
        
        .product-price {
            font-weight: bold;
            color: var(--primary);
            margin: 10px 0;
            font-size: 1.2rem;
        }
        
        .add-to-cart {
            background-color: var(--primary);
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
            transition: background-color 0.3s;
            font-size: 1rem;
        }
        
        .add-to-cart:hover {
            background-color: var(--primary-dark);
        }
        
        .products-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .section-title {
            margin: 30px 0 15px;
            font-size: 1.5rem;
            color: var(--dark);
            position: relative;
            padding-bottom: 10px;
        }
        
        .section-title::after {
            content: '';
            position: absolute;
            bottom: 0;
            right: 0;
            width: 50px;
            height: 3px;
            background-color: var(--primary);
        }
        
        /* التذييل */
        .footer {
            background-color: var(--dark);
            color: white;
            padding: 40px 0 20px;
            margin-top: 50px;
        }
        
        .footer-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 30px;
        }
        
        .footer-col h3 {
            margin-bottom: 20px;
            font-size: 1.2rem;
        }
        
        .footer-col ul li {
            margin-bottom: 10px;
        }
        
        .footer-col ul li a:hover {
            color: var(--accent);
        }
        
        .social-links {
            display: flex;
            gap: 15px;
        }
        
        .social-links a {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            background-color: rgba(255,255,255,0.1);
            border-radius: 50%;
            transition: background-color 0.3s;
        }
        
        .social-links a:hover {
            background-color: var(--primary);
        }
        
        .copyright {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        
        /* التجاوب مع مختلف الشاشات */
        @media (max-width: 992px) {
            .search-bar {
                margin: 0 10px;
            }
            
            .user-menu span {
                display: none;
            }
        }
        
        @media (max-width: 768px) {
            .mobile-menu-toggle {
                display: block;
            }
            
            .user-menu {
                display: none;
            }
            
            .search-bar {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                margin: 0;
                padding: 10px;
                background-color: var(--primary);
                display: none;
            }
            
            .search-bar.active {
                display: block;
            }
        }
        
        /* نماذج الدخول */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
            z-index: 1002;
            justify-content: center;
            align-items: center;
        }
        
        .modal-content {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            width: 100%;
            max-width: 400px;
            position: relative;
        }
        
        .close-modal {
            position: absolute;
            top: 10px;
            left: 10px;
            font-size: 1.5rem;
            cursor: pointer;
        }
        
        .modal h3 {
            margin-bottom: 20px;
            text-align: center;
        }
        
        .modal input {
            width: 100%;
            padding: 12px 15px;
            margin-bottom: 15px;
            border: 1px solid var(--light-gray);
            border-radius: 4px;
            font-size: 1rem;
        }
        
        .modal button[type="submit"] {
            width: 100%;
            padding: 12px;
            background-color: var(--primary);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
            transition: background-color 0.3s;
        }
        
        .modal button[type="submit"]:hover {
            background-color: var(--primary-dark);
        }
        
        .modal p {
            text-align: center;
            margin-top: 15px;
        }
        
        .modal p a {
            color: var(--primary);
            font-weight: bold;
        }
        
        /* الإشعارات */
        .notification {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: var(--primary);
            color: white;
            padding: 15px 20px;
            border-radius: 4px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.2);
            z-index: 1003;
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from { transform: translateY(100px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap" rel="stylesheet">
</head>
<body>
    <!-- الهيكل الأساسي للموقع -->
    <header class="header">
        <div class="container">
            <a href="/" class="logo">Zent Shop</a>
            
            <div class="search-bar">
                <form id="searchForm">
                    <input type="search" id="searchInput" placeholder="ابحث عن منتجات...">
                    <button type="submit"><i class="fas fa-search"></i></button>
                </form>
            </div>
            
            <nav class="user-menu">
                <a href="#" id="userAccount"><i class="fas fa-user"></i> <span>حسابي</span></a>
                <a href="#" id="userOrders"><i class="fas fa-box-open"></i> <span>طلباتي</span></a>
                <a href="#" id="userWishlist"><i class="fas fa-heart"></i> <span>المفضلة</span></a>
                <a href="#" id="cartLink" class="cart-link">
                    <i class="fas fa-shopping-cart"></i>
                    <span class="cart-count">0</span>
                    <span>السلة</span>
                </a>
            </nav>
            
            <button class="mobile-menu-toggle" id="mobileMenuToggle">
                <i class="fas fa-bars"></i>
            </button>
        </div>
    </header>

    <!-- القائمة الجانبية للجوّال -->
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <h3>القائمة الرئيسية</h3>
            <button class="close-sidebar" id="closeSidebar">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <ul class="mobile-menu">
            <li><a href="/">الرئيسية</a></li>
            <li><a href="#" id="mobileProducts">المنتجات</a></li>
            <li><a href="#" id="mobileCategories">التصنيفات</a></li>
            <li><a href="#" id="mobileAccount">حسابي</a></li>
            <li><a href="#" id="mobileCart">سلة التسوق</a></li>
        </ul>
    </aside>

    <!-- المحتوى الرئيسي -->
    <main class="main-content">
        <div class="container">
            <!-- قسم العروض المميزة -->
            <section class="featured-products">
                <h2 class="section-title">منتجات مميزة</h2>
                <div class="products-grid" id="featuredProducts">
                    <!-- سيتم ملؤها بالمنتجات عبر JavaScript -->
                </div>
            </section>
            
            <!-- قسم المنتجات الجديدة -->
            <section class="new-products">
                <h2 class="section-title">وصل حديثاً</h2>
                <div class="products-grid" id="newProducts">
                    <!-- سيتم ملؤها بالمنتجات عبر JavaScript -->
                </div>
            </section>
        </div>
    </main>

    <!-- التذييل -->
    <footer class="footer">
        <div class="container">
            <div class="footer-grid">
                <div class="footer-col">
                    <h3>عن المتجر</h3>
                    <p>Zent Shop هو متجر إلكتروني رائد في العالم العربي، نقدم أفضل المنتجات بأفضل الأسعار.</p>
                </div>
                <div class="footer-col">
                    <h3>روابط سريعة</h3>
                    <ul>
                        <li><a href="/">الرئيسية</a></li>
                        <li><a href="#" id="footerProducts">المنتجات</a></li>
                        <li><a href="#" id="footerAbout">عن المتجر</a></li>
                        <li><a href="#" id="footerContact">اتصل بنا</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h3>وسائل التواصل</h3>
                    <div class="social-links">
                        <a href="#"><i class="fab fa-facebook-f"></i></a>
                        <a href="#"><i class="fab fa-twitter"></i></a>
                        <a href="#"><i class="fab fa-instagram"></i></a>
                    </div>
                </div>
            </div>
            <div class="copyright">
                <p>&copy; <span id="currentYear"></span> Zent Shop. جميع الحقوق محفوظة.</p>
            </div>
        </div>
    </footer>

    <!-- نماذج الدخول -->
    <div class="modal" id="loginModal">
        <div class="modal-content">
            <span class="close-modal">&times;</span>
            <h3>تسجيل الدخول</h3>
            <form id="loginForm">
                <input type="email" id="loginEmail" placeholder="البريد الإلكتروني" required>
                <input type="password" id="loginPassword" placeholder="كلمة المرور" required>
                <button type="submit">تسجيل الدخول</button>
            </form>
            <p>ليس لديك حساب؟ <a href="#" id="showRegister">سجل الآن</a></p>
        </div>
    </div>
    
    <div class="modal" id="registerModal">
        <div class="modal-content">
            <span class="close-modal">&times;</span>
            <h3>تسجيل حساب جديد</h3>
            <form id="registerForm">
                <input type="text" id="registerName" placeholder="الاسم الكامل" required>
                <input type="email" id="registerEmail" placeholder="البريد الإلكتروني" required>
                <input type="password" id="registerPassword" placeholder="كلمة المرور" required>
                <button type="submit">تسجيل</button>
            </form>
        </div>
    </div>

    <!-- JavaScript -->
    <script>
        // بيانات التطبيق
        const App = {
            cart: [],
            products: [],
            user: null,
            
            // تهيئة التطبيق
            init() {
                this.setupEventListeners();
                this.loadProducts();
                this.updateCartCount();
                this.setCurrentYear();
                this.checkAuth();
            },
            
            // إعداد مستمعي الأحداث
            setupEventListeners() {
                // القوائم المتنقلة
                document.getElementById('mobileMenuToggle').addEventListener('click', () => {
                    document.getElementById('sidebar').classList.add('active');
                });
                
                document.getElementById('closeSidebar').addEventListener('click', () => {
                    document.getElementById('sidebar').classList.remove('active');
                });
                
                // البحث
                document.getElementById('searchForm').addEventListener('submit', (e) => {
                    e.preventDefault();
                    const query = document.getElementById('searchInput').value;
                    this.searchProducts(query);
                });
                
                // أحداث السلة
                document.addEventListener('click', (e) => {
                    if (e.target.classList.contains('add-to-cart') || e.target.closest('.add-to-cart')) {
                        const button = e.target.classList.contains('add-to-cart') ? e.target : e.target.closest('.add-to-cart');
                        const productId = parseInt(button.dataset.id);
                        this.addToCart(productId);
                    }
                });
                
                // أحداث الروابط المشتركة
                const linkIds = ['mobileProducts', 'mobileAccount', 'mobileCart', 
                                 'footerProducts', 'footerAbout', 'footerContact',
                                 'userAccount', 'userOrders', 'userWishlist', 'cartLink'];
                
                linkIds.forEach(id => {
                    const element = document.getElementById(id);
                    if (element) {
                        element.addEventListener('click', (e) => {
                            e.preventDefault();
                            this.handleLinkClick(id);
                        });
                    }
                });
                
                // أحداث النماذج
                document.getElementById('showRegister')?.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.showModal('registerModal');
                });
                
                document.querySelectorAll('.close-modal').forEach(btn => {
                    btn.addEventListener('click', () => {
                        this.hideAllModals();
                    });
                });
                
                document.getElementById('loginForm')?.addEventListener('submit', (e) => {
                    e.preventDefault();
                    const email = document.getElementById('loginEmail').value;
                    const password = document.getElementById('loginPassword').value;
                    this.login(email, password);
                });
                
                document.getElementById('registerForm')?.addEventListener('submit', (e) => {
                    e.preventDefault();
                    const name = document.getElementById('registerName').value;
                    const email = document.getElementById('registerEmail').value;
                    const password = document.getElementById('registerPassword').value;
                    this.register(name, email, password);
                });
                
                // إغلاق النماذج بالنقر خارجها
                document.querySelectorAll('.modal').forEach(modal => {
                    modal.addEventListener('click', (e) => {
                        if (e.target === modal) {
                            this.hideAllModals();
                        }
                    });
                });
            },
            
            // تحميل المنتجات من الخادم
            async loadProducts() {
                try {
                    const response = await fetch('/api/products');
                    const data = await response.json();
                    
                    if (data.success) {
                        this.products = data.products;
                        this.renderProducts();
                    }
                } catch (error) {
                    console.error('Error loading products:', error);
                    this.showNotification('حدث خطأ أثناء تحميل المنتجات', 'error');
                }
            },
            
            // عرض المنتجات
            renderProducts() {
                const featuredContainer = document.getElementById('featuredProducts');
                const newContainer = document.getElementById('newProducts');
                
                const featuredProducts = this.products.filter(p => p.is_featured);
                const newProducts = this.products.slice(0, 4); // أول 4 منتجات كمنتجات جديدة
                
                featuredContainer.innerHTML = featuredProducts.map(product => this.createProductCard(product)).join('');
                newContainer.innerHTML = newProducts.map(product => this.createProductCard(product)).join('');
            },
            
            // إنشاء بطاقة منتج
            createProductCard(product) {
                return `
                    <div class="product-card">
                        <div class="product-image">
                            <img src="${product.image}" alt="${product.name}" loading="lazy">
                        </div>
                        <div class="product-info">
                            <h3>${product.name}</h3>
                            <div class="product-price">
                                <span class="price">${product.price} ر.س</span>
                            </div>
                            <button class="add-to-cart" data-id="${product.id}">أضف إلى السلة</button>
                        </div>
                    </div>
                `;
            },
            
            // إضافة إلى السلة
            async addToCart(productId) {
                if (!this.user) {
                    this.showNotification('يجب تسجيل الدخول أولاً', 'error');
                    this.showModal('loginModal');
                    return;
                }
                
                try {
                    const response = await fetch('/api/cart', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            product_id: productId,
                            user_id: this.user.id
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        this.cart = data.cart;
                        this.updateCartCount();
                        const product = this.products.find(p => p.id == productId);
                        this.showNotification(`تمت إضافة ${product.name} إلى السلة`);
                    } else {
                        this.showNotification(data.message || 'حدث خطأ أثناء إضافة المنتج', 'error');
                    }
                } catch (error) {
                    console.error('Error adding to cart:', error);
                    this.showNotification('حدث خطأ أثناء إضافة المنتج', 'error');
                }
            },
            
            // تحديث عداد السلة
            updateCartCount() {
                const count = this.cart.reduce((total, item) => total + (item.quantity || 1), 0);
                document.querySelectorAll('.cart-count').forEach(el => {
                    el.textContent = count;
                });
            },
            
            // البحث عن المنتجات
            searchProducts(query) {
                if (query.trim() === '') return;
                
                const results = this.products.filter(product => 
                    product.name.includes(query) || 
                    (product.description && product.description.includes(query))
                );
                
                this.showNotification(`عرض ${results.length} نتيجة للبحث عن "${query}"`);
                // في الواقع سيتم توجيه المستخدم لصفحة نتائج البحث
            },
            
            // التحقق من المصادقة
            async checkAuth() {
                try {
                    const token = localStorage.getItem('authToken');
                    if (token) {
                        // في الواقع سيتم التحقق من الخادم
                        const user = DB.users.find(u => u.token === token);
                        if (user) {
                            this.user = user;
                            this.updateAuthUI();
                            await this.loadCart();
                        }
                    }
                } catch (error) {
                    console.error('Error checking auth:', error);
                }
            },
            
            // تسجيل الدخول
            async login(email, password) {
                try {
                    const response = await fetch('/api/auth/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            email: email,
                            password: password
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        this.user = data.user;
                        localStorage.setItem('authToken', data.token);
                        this.updateAuthUI();
                        this.hideAllModals();
                        this.showNotification(`مرحباً ${this.user.name}`);
                        await this.loadCart();
                    } else {
                        this.showNotification(data.message || 'بيانات الدخول غير صحيحة', 'error');
                    }
                } catch (error) {
                    console.error('Error logging in:', error);
                    this.showNotification('حدث خطأ أثناء تسجيل الدخول', 'error');
                }
            },
            
            // التسجيل
            async register(name, email, password) {
                try {
                    const response = await fetch('/api/auth/register', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            name: name,
                            email: email,
                            password: password
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        this.showNotification('تم إنشاء الحساب بنجاح، يرجى تسجيل الدخول');
                        this.hideAllModals();
                        this.showModal('loginModal');
                    } else {
                        this.showNotification(data.message || 'حدث خطأ أثناء التسجيل', 'error');
                    }
                } catch (error) {
                    console.error('Error registering:', error);
                    this.showNotification('حدث خطأ أثناء التسجيل', 'error');
                }
            },
            
            // تحميل السلة
            async loadCart() {
                if (!this.user) return;
                
                try {
                    const response = await fetch(`/api/cart?user_id=${this.user.id}`);
                    const data = await response.json();
                    
                    if (data.success) {
                        this.cart = data.cart || [];
                        this.updateCartCount();
                    }
                } catch (error) {
                    console.error('Error loading cart:', error);
                }
            },
            
            // تحديث واجهة المستخدم حسب حالة المصادقة
            updateAuthUI() {
                if (this.user) {
                    document.getElementById('userAccount').querySelector('span').textContent = this.user.name;
                }
            },
            
            // عرض الإشعارات
            showNotification(message, type = 'success') {
                const notification = document.createElement('div');
                notification.className = `notification ${type}`;
                notification.textContent = message;
                document.body.appendChild(notification);
                
                setTimeout(() => {
                    notification.remove();
                }, 3000);
            },
            
            // إدارة النقر على الروابط
            handleLinkClick(linkId) {
                const actions = {
                    'userAccount': () => this.showAuthModal(),
                    'cartLink': () => this.showCart(),
                    'mobileAccount': () => this.showAuthModal(),
                    'mobileCart': () => this.showCart(),
                    // يمكن إضافة المزيد من الإجراءات هنا
                };
                
                if (actions[linkId]) {
                    actions[linkId]();
                } else {
                    this.showNotification(`سيتم توجيهك إلى ${linkId.replace('mobile', '').replace('footer', '')}`);
                }
            },
            
            // عرض سلة التسوق
            showCart() {
                if (!this.user) {
                    this.showNotification('يجب تسجيل الدخول أولاً', 'error');
                    this.showModal('loginModal');
                    return;
                }
                
                if (this.cart.length === 0) {
                    this.showNotification('سلة التسوق فارغة');
                } else {
                    this.showNotification(`عرض سلة التسوق (${this.cart.length} عنصر)`);
                    // في الواقع سيتم توجيه المستخدم لصفحة السلة
                }
            },
            
            // عرض نموذج المصادقة
            showAuthModal() {
                if (this.user) {
                    this.showNotification(`مرحباً ${this.user.name}`);
                } else {
                    this.showModal('loginModal');
                }
            },
            
            // عرض نموذج
            showModal(modalId) {
                this.hideAllModals();
                document.getElementById(modalId).style.display = 'flex';
            },
            
            // إخفاء جميع النماذج
            hideAllModals() {
                document.querySelectorAll('.modal').forEach(modal => {
                    modal.style.display = 'none';
                });
            },
            
            // تعيين السنة الحالية في التذييل
            setCurrentYear() {
                document.getElementById('currentYear').textContent = new Date().getFullYear();
            }
        };
        
        // بدء تشغيل التطبيق
        document.addEventListener('DOMContentLoaded', () => {
            App.init();
        });
    </script>
</body>
</html>
"""

# ========== واجهات API ==========
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify({
        "success": True,
        "products": DB["products"]
    })

@app.route('/api/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"success": False, "message": "معرف المستخدم مطلوب"}), 400
        
        user_cart = [item for item in DB["orders"] if item.get("user_id") == int(user_id)]
        return jsonify({
            "success": True,
            "cart": user_cart
        })
    
    elif request.method == 'POST':
        data = request.json
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        
        if not user_id or not product_id:
            return jsonify({"success": False, "message": "بيانات غير مكتملة"}), 400
        
        product = next((p for p in DB["products"] if p["id"] == product_id), None)
        if not product:
            return jsonify({"success": False, "message": "المنتج غير موجود"}), 404
        
        # إضافة الطلب إلى قاعدة البيانات
        order = {
            "id": len(DB["orders"]) + 1,
            "user_id": int(user_id),
            "product_id": product_id,
            "quantity": 1,
            "date": datetime.now().isoformat(),
            "status": "in_cart"
        }
        
        DB["orders"].append(order)
        
        return jsonify({
            "success": True,
            "message": "تمت إضافة المنتج إلى السلة",
            "cart": [order]
        })

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"success": False, "message": "بيانات غير مكتملة"}), 400
    
    # في الواقع سيتم التحقق من قاعدة البيانات مع تشفير كلمة المرور
    user = next((u for u in DB["users"] if u["email"] == email and u["password"] == password), None)
    if user:
        token = f"token_{user['id']}_{datetime.now().timestamp()}"
        user["token"] = token
        return jsonify({
            "success": True,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            },
            "token": token
        })
    return jsonify({"success": False, "message": "بيانات الدخول غير صحيحة"}), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({"success": False, "message": "بيانات غير مكتملة"}), 400
    
    if any(u["email"] == email for u in DB["users"]):
        return jsonify({"success": False, "message": "البريد الإلكتروني مستخدم بالفعل"}), 400
    
    new_user = {
        "id": len(DB["users"]) + 1,
        "name": name,
        "email": email,
        "password": password,
        "created_at": datetime.now().isoformat()
    }
    DB["users"].append(new_user)
    
    return jsonify({
        "success": True,
        "message": "تم إنشاء الحساب بنجاح"
    })

# الاتصال بقاعدة البيانات باستخدام متغير البيئة
client = MongoClient(os.environ.get('mongodb://mongo:rlHwuXyhnLdaZylWJKRFhwhWXtbMcSts@switchyard.proxy.rlwy.net:50008'))
db = client['zent_shop']
products_collection = db['products']

@app.route('/')
def index():
    products = list(products_collection.find())
    return render_template('index.html', products=products)

@app.route('/add-product', methods=['POST'])
def add_product():
    name = request.form['name']
    price = float(request.form['price'])
    products_collection.insert_one({'name': name, 'price': price})
    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

