
import { useEffect, useRef, useState } from "react";
import './App.css';

import LoginPage from './pages/Login';
import RegisterPage from './pages/Register';
import ContactPage from './pages/Contact';
import AccountPage from './pages/Account';
import AdminPage from './pages/Admin';
import ShelfPage from './pages/Shelf';
import LoansPage from './pages/Loans';
import ResourceModal from './components/ResourceModal';
import ResourceCard from './components/ResourceCard';
import AnimatedCounter from './components/AnimatedCounter';
import ThemeToggle from './components/ThemeToggle';
import useReveal from './hooks/useReveal';
import useMotionEffects from './hooks/useMotionEffects';
import { apiRequest } from './services/api';
import libraryPhoto from './assets/library-hero.jpg';

// Small floating confirmation used for favourite and session actions.
function Toast({ toast }) {

  if (!toast) {
    return null;
  }

  return (
    <div className="toast" role="status" key={toast.key}>
      <span className="toast-dot" aria-hidden="true" />
      <span>{toast.message}</span>
    </div>
  );
}

// Number of catalogue items fetched per batch.
const PAGE_SIZE = 12;

function App() {
  // Search input.
  const [search, setSearch] = useState('');

  // Categories from the database.
  const [categories, setCategories] = useState([]);

  // Resources from the database.
  const [resources, setResources] = useState([]);

  // Paging for the catalogue: total matches and whether more exist.
  const [totalResources, setTotalResources] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);

  // Currently selected category.
  const [activeCategory, setActiveCategory] = useState('');

  // Selected resource type (empty means all).
  const [resourceType, setResourceType] = useState('');

  // Resource opened in the detail modal.
  const [selectedResource, setSelectedResource] = useState(null);

  // Page navigation.
  const [currentPage, setCurrentPage] = useState('home');

  // Authenticated user.
  const [currentUser, setCurrentUser] = useState(null);

  // Saved resources for the signed-in member.
  const [favorites, setFavorites] = useState([]);
  const [favoritesLoading, setFavoritesLoading] = useState(false);

  // Active book loans for the signed-in member.
  const [loans, setLoans] = useState([]);

  // Public library statistics.
  const [stats, setStats] = useState(null);

  // Colour theme (light or dark).
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('elib-theme');

    if (saved === 'dark' || saved === 'light') {
      return saved;
    }

    return window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';
  });

  // Toast notification.
  const [toast, setToast] = useState(null);

  // Navbar glass effect once the page is scrolled.
  const [scrolled, setScrolled] = useState(false);

  // Mobile navigation drawer and the signed-in member menu.
  const [menuOpen, setMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  // Loading and error states.
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const searchRef = useRef(null);
  const headerRef = useRef(null);
  const userMenuRef = useRef(null);

  // Reveal on-scroll animations for newly rendered content.
  useReveal();

  // Scroll progress, card tilt, hero spotlight and button ripples.
  useMotionEffects();

  // Apply and remember the selected theme.
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem('elib-theme', theme);
  }, [theme]);

  // Close the toast automatically.
  useEffect(() => {
    if (!toast) {
      return undefined;
    }

    const timer = setTimeout(() => setToast(null), 4200);

    return () => clearTimeout(timer);
  }, [toast]);

  // Track scrolling for the translucent navbar.
  useEffect(() => {
    function handleScroll() {
      setScrolled(window.scrollY > 12);
    }

    handleScroll();

    window.addEventListener('scroll', handleScroll, { passive: true });

    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close the navigation drawer and member menu on outside click / Escape.
  useEffect(() => {
    function handlePointerDown(event) {
      if (headerRef.current && !headerRef.current.contains(event.target)) {
        setMenuOpen(false);
      }

      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setUserMenuOpen(false);
      }
    }

    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        setMenuOpen(false);
        setUserMenuOpen(false);
      }
    }

    window.addEventListener('pointerdown', handlePointerDown);
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('pointerdown', handlePointerDown);
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  // Press "/" anywhere to jump to the search box.
  useEffect(() => {
    function handleKeyDown(event) {
      if (event.key !== '/' || currentPage !== 'home') {
        return;
      }

      const active = document.activeElement;

      if (
        active
        && (
          active.tagName === 'INPUT'
          || active.tagName === 'TEXTAREA'
          || active.isContentEditable
        )
      ) {
        return;
      }

      event.preventDefault();
      searchRef.current?.focus();
    }

    window.addEventListener('keydown', handleKeyDown);

    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentPage]);

  // Restore existing login session.
  useEffect(() => {
    apiRequest('/api/auth/me')
      .then((result) => {
        setCurrentUser(result.user);
      })
      .catch(() => {
        // Visitor is not logged in.
      });
  }, []);

  // Fetch categories from Flask.
  useEffect(() => {
    apiRequest('/api/categories')
      .then((result) => {
        setCategories(result.categories || []);
      })
      .catch((err) => {
        console.error('Category loading error:', err);
        setError('Could not load library categories.');
      });
  }, []);

  // Fetch public statistics for the hero and stats band.
  useEffect(() => {
    apiRequest('/api/stats')
      .then((result) => {
        setStats(result.stats);
      })
      .catch((err) => {
        console.error('Stats loading error:', err);
      });
  }, []);

  // Load the member's saved shelf.
  useEffect(() => {
    if (!currentUser) {
      return undefined;
    }

    let cancelled = false;

    setFavoritesLoading(true);

    apiRequest('/api/favorites')
      .then((result) => {
        if (!cancelled) {
          setFavorites(result.favorites || []);
        }
      })
      .catch((err) => {
        console.error('Shelf loading error:', err);
      })
      .finally(() => {
        if (!cancelled) {
          setFavoritesLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [currentUser]);

  // Load the member's active book loans.
  useEffect(() => {
    if (!currentUser) {
      return undefined;
    }

    let cancelled = false;

    apiRequest('/api/loans/mine')
      .then((result) => {
        if (!cancelled) {
          setLoans(result.active || []);
        }
      })
      .catch((err) => {
        console.error('Loans loading error:', err);
      });

    return () => {
      cancelled = true;
    };
  }, [currentUser]);

  // Fetch the first page of resources from Flask.
  useEffect(() => {
    let cancelled = false;

    async function loadResources() {
      setLoading(true);
      setError('');

      try {
        const result = await apiRequest(
          `/api/resources?${catalogueQuery(0, PAGE_SIZE)}`
        );

        if (!cancelled) {
          setResources(result.resources || []);
          setTotalResources(result.total ?? (result.resources || []).length);
          setHasMore(Boolean(result.has_more));
        }

      } catch (err) {
        console.error('Resource loading error:', err);

        if (!cancelled) {
          setError('Could not load library resources.');
        }

      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadResources();

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search, activeCategory, resourceType]);

  // Current search and filters as a query string.
  function catalogueQuery(offset, limit) {
    const params = new URLSearchParams();

    if (search.trim()) {
      params.set('search', search.trim());
    }

    if (activeCategory) {
      params.set('category_id', activeCategory);
    }

    if (resourceType) {
      params.set('resource_type', resourceType);
    }

    params.set('offset', String(offset));
    params.set('limit', String(limit));

    return params.toString();
  }

  // Fetch the next batch (or everything left) only when asked.
  async function loadMore(showAll = false) {
    setLoadingMore(true);

    try {
      const limit = showAll
        ? Math.max(totalResources - resources.length, 1)
        : PAGE_SIZE;

      const result = await apiRequest(
        `/api/resources?${catalogueQuery(resources.length, limit)}`
      );

      setResources((current) => {
        const seen = new Set(current.map((item) => item.id));
        return [
          ...current,
          ...(result.resources || []).filter((item) => !seen.has(item.id))
        ];
      });
      setTotalResources(result.total ?? totalResources);
      setHasMore(Boolean(result.has_more));

    } catch (err) {
      showToast(err.message || 'Could not load more resources.');
    } finally {
      setLoadingMore(false);
    }
  }

  function showLess() {
    setResources((current) => current.slice(0, PAGE_SIZE));
    setHasMore(totalResources > PAGE_SIZE);
    document
      .getElementById('catalogue')
      ?.scrollIntoView({ behavior: 'smooth' });
  }

  // Saved resource ids for quick lookup.
  const favoriteIds = new Set(favorites.map((item) => item.id));

  const hasFilters = Boolean(search.trim() || activeCategory || resourceType);

  function showToast(message) {
    setToast({ message, key: Date.now() });
  }

  function toggleTheme() {
    setTheme((value) => (value === 'dark' ? 'light' : 'dark'));
  }

  function resetFilters() {
    setSearch('');
    setActiveCategory('');
    setResourceType('');
  }

  // Save or remove a resource with an optimistic update.
  async function toggleFavorite(resource) {
    if (!currentUser) {
      showToast('Log in to save books to your shelf.');
      setCurrentPage('login');
      return;
    }

    const saved = favoriteIds.has(resource.id);

    setFavorites((current) =>
      saved
        ? current.filter((item) => item.id !== resource.id)
        : [resource, ...current]
    );

    try {
      const result = await apiRequest(
        `/api/favorites/${resource.id}`,
        { method: saved ? 'DELETE' : 'POST' }
      );

      showToast(result.message || 'Your shelf was updated.');

    } catch (err) {
      setFavorites((current) =>
        saved
          ? [resource, ...current]
          : current.filter((item) => item.id !== resource.id)
      );

      showToast(err.message || 'Could not update your shelf.');
    }
  }

  // The member's active loan for a resource, if any.
  function activeLoanFor(resourceId) {
    return loans.find((loan) => loan.resource.id === resourceId);
  }

  // Borrow a book with a 14-day loan period.
  async function borrowResource(resource) {
    if (!currentUser) {
      showToast('Log in to borrow books.');
      setCurrentPage('login');
      return;
    }

    try {
      const result = await apiRequest('/api/loans', {
        method: 'POST',
        body: JSON.stringify({ resource_id: resource.id })
      });

      setLoans((current) => [result.loan, ...current]);
      showToast(result.message || 'Book borrowed. Enjoy!');

    } catch (err) {
      showToast(err.message || 'Could not borrow this book.');
    }
  }

  // Return a borrowed book.
  async function returnLoan(loan) {
    const result = await apiRequest(`/api/loans/${loan.id}/return`, {
      method: 'POST'
    });

    setLoans((current) =>
      current.filter((item) => item.id !== loan.id)
    );

    showToast(result.message || 'Book returned.');
  }

  // Logout functionality.
  const handleLogout = async () => {
    try {
      await apiRequest('/api/auth/logout', {
        method: 'POST'
      });

      setCurrentUser(null);
      setFavorites([]);
      setLoans([]);
      setUserMenuOpen(false);
      setMenuOpen(false);
      setCurrentPage('home');
      showToast('You have logged out.');

    } catch (err) {
      showToast(err.message || 'Logout failed.');
    }
  };

  const themeToggle = (
    <ThemeToggle theme={theme} onToggle={toggleTheme} />
  );

  // Display contact page.
  if (currentPage === 'contact') {
    return (
      <ContactPage onHome={() => setCurrentPage('home')} />
    );
  }

  // Display account page for logged-in members.
  if (currentPage === 'account') {
    if (!currentUser) {
      setCurrentPage('login');
      return null;
    }

    return (
      <AccountPage
        currentUser={currentUser}
        onHome={() => setCurrentPage('home')}
        onShelf={() => setCurrentPage('shelf')}
        favoriteCount={favorites.length}
        theme={theme}
        onToggleTheme={toggleTheme}
      />
    );
  }

  // Display the member's saved shelf.
  if (currentPage === 'shelf') {
    if (!currentUser) {
      setCurrentPage('login');
      return null;
    }

    return (
      <>
        <ShelfPage
          currentUser={currentUser}
          resources={favorites}
          loading={favoritesLoading}
          onHome={() => setCurrentPage('home')}
          onOpen={setSelectedResource}
          onFavorite={toggleFavorite}
        />

        {selectedResource && (
          <ResourceModal
            resource={selectedResource}
            currentUser={currentUser}
            isFavorite={favoriteIds.has(selectedResource.id)}
            onFavorite={toggleFavorite}
            isBorrowed={Boolean(activeLoanFor(selectedResource.id))}
            borrowedLoan={activeLoanFor(selectedResource.id)}
            onBorrow={borrowResource}
            onClose={() => setSelectedResource(null)}
          />
        )}

        <Toast toast={toast} />
      </>
    );
  }

  // Display the member's borrowed books.
  if (currentPage === 'loans') {
    if (!currentUser) {
      setCurrentPage('login');
      return null;
    }

    return (
      <>
        <LoansPage
          currentUser={currentUser}
          onHome={() => setCurrentPage('home')}
          onOpen={setSelectedResource}
          onReturn={returnLoan}
        />

        {selectedResource && (
          <ResourceModal
            resource={selectedResource}
            currentUser={currentUser}
            isFavorite={favoriteIds.has(selectedResource.id)}
            onFavorite={toggleFavorite}
            isBorrowed={Boolean(activeLoanFor(selectedResource.id))}
            borrowedLoan={activeLoanFor(selectedResource.id)}
            onBorrow={borrowResource}
            onClose={() => setSelectedResource(null)}
          />
        )}

        <Toast toast={toast} />
      </>
    );
  }

  // Display the administration dashboard.
  if (currentPage === 'admin') {
    if (!currentUser) {
      setCurrentPage('login');
      return null;
    }

    if (currentUser.role !== 'admin') {
      setCurrentPage('home');
      return null;
    }

    return (
      <AdminPage
        currentUser={currentUser}
        theme={theme}
        onToggleTheme={toggleTheme}
        onHome={() => setCurrentPage('home')}
        onLogout={handleLogout}
        onUserUpdated={setCurrentUser}
      />
    );
  }

  // Display registration page.
  if (currentPage === 'register') {
    return (
      <RegisterPage
        onHome={() => setCurrentPage('home')}
        onLogin={() => setCurrentPage('login')}
      />
    );
  }

  // Display login page.
  if (currentPage === 'login') {
    return (
      <>
        <LoginPage
          onHome={() => setCurrentPage('home')}
          onRegister={() => setCurrentPage('register')}
          onLoggedIn={(user) => {
            setCurrentUser(user);
            setCurrentPage('home');
            showToast(`Welcome back, ${user.full_name}!`);
          }}
        />

        <Toast toast={toast} />
      </>
    );
  }

  return (
    <div className={currentPage === 'home' ? 'app app-home' : 'app'}>

      {/* Navigation bar */}
      <header
        className={scrolled ? 'navbar is-scrolled' : 'navbar'}
        ref={headerRef}
      >

        <a
          href="#home"
          className="brand"
          onClick={() => setMenuOpen(false)}
        >
          <span className="brand-icon">E</span>
          <span>E-Library</span>
        </a>

        <button
          type="button"
          className={menuOpen ? 'nav-toggle is-open' : 'nav-toggle'}
          aria-expanded={menuOpen}
          aria-controls="primary-menu"
          aria-label="Toggle navigation"
          onClick={() => setMenuOpen((open) => !open)}
        >
          <span />
          <span />
          <span />
        </button>

        <div
          id="primary-menu"
          className={menuOpen ? 'nav-menu is-open' : 'nav-menu'}
        >

          <nav className="nav-links">
            <a href="#home" onClick={() => setMenuOpen(false)}>Home</a>
            <a href="#categories" onClick={() => setMenuOpen(false)}>Categories</a>
            <a href="#catalogue" onClick={() => setMenuOpen(false)}>Books</a>
            <a href="#about" onClick={() => setMenuOpen(false)}>About</a>

            <button
              type="button"
              className="nav-link"
              onClick={() => {
                setMenuOpen(false);
                setCurrentPage('contact');
              }}
            >
              Contact
            </button>
          </nav>

          <div className="nav-actions">

            <a
              href="#catalogue"
              className="nav-button"
              onClick={() => setMenuOpen(false)}
            >
              Explore Library
            </a>

            {themeToggle}

            {currentUser ? (
              <div className="user-menu" ref={userMenuRef}>
                <button
                  type="button"
                  className={
                    userMenuOpen
                      ? 'user-menu-trigger is-open'
                      : 'user-menu-trigger'
                  }
                  aria-expanded={userMenuOpen}
                  aria-haspopup="menu"
                  onClick={() => setUserMenuOpen((open) => !open)}
                >
                  <span className="user-menu-name">
                    Hi, {currentUser.full_name}
                  </span>
                  <svg
                    className="user-menu-caret"
                    viewBox="0 0 12 8"
                    aria-hidden="true"
                  >
                    <path
                      d="M1 1.5 6 6.5 11 1.5"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.8"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </button>

                {userMenuOpen && (
                  <div className="user-menu-panel" role="menu">
                    {currentUser.role === 'admin' && (
                      <button
                        type="button"
                        role="menuitem"
                        className="user-menu-item"
                        onClick={() => {
                          setUserMenuOpen(false);
                          setCurrentPage('admin');
                        }}
                      >
                        Admin
                      </button>
                    )}

                    <button
                      type="button"
                      role="menuitem"
                      className="user-menu-item"
                      onClick={() => {
                        setUserMenuOpen(false);
                        setCurrentPage('shelf');
                      }}
                    >
                      My Shelf
                      {favorites.length > 0 && (
                        <span className="nav-badge">{favorites.length}</span>
                      )}
                    </button>

                    <button
                      type="button"
                      role="menuitem"
                      className="user-menu-item"
                      onClick={() => {
                        setUserMenuOpen(false);
                        setCurrentPage('loans');
                      }}
                    >
                      My Loans
                      {loans.length > 0 && (
                        <span className="nav-badge">{loans.length}</span>
                      )}
                    </button>

                    <button
                      type="button"
                      role="menuitem"
                      className="user-menu-item"
                      onClick={() => {
                        setUserMenuOpen(false);
                        setCurrentPage('account');
                      }}
                    >
                      Account
                    </button>

                    <button
                      type="button"
                      role="menuitem"
                      className="user-menu-item is-danger"
                      onClick={() => {
                        setUserMenuOpen(false);
                        handleLogout();
                      }}
                    >
                      Logout
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <>
                <button
                  className="auth-nav-button"
                  onClick={() => setCurrentPage('login')}
                >
                  Login
                </button>

                <button
                  className="auth-nav-button auth-nav-primary"
                  onClick={() => setCurrentPage('register')}
                >
                  Register
                </button>
              </>
            )}

          </div>
        </div>
      </header>

      <main>

        {/* Homepage hero */}
        <section
          className="hero hero-photo"
          id="home"
          style={{ '--hero-photo': `url(${libraryPhoto})` }}
        >

          <span className="hero-orb orb-one" aria-hidden="true" />
          <span className="hero-orb orb-two" aria-hidden="true" />
          <span className="hero-orb orb-three" aria-hidden="true" />

          <div className="hero-content reveal">

            <span className="eyebrow">
              YOUR DIGITAL LEARNING SPACE
            </span>

            <h1 className="hero-title">
              <span className="word" style={{ '--i': 0 }}>A</span>
              <span className="word" style={{ '--i': 1 }}>world</span>
              <span className="word" style={{ '--i': 2 }}>of</span>
              <span className="word" style={{ '--i': 3 }}>knowledge,</span>
              <span className="hero-accent">
                <span className="word accent-word" style={{ '--i': 4 }}>just</span>
                <span className="word accent-word" style={{ '--i': 5 }}>a</span>
                <span className="word accent-word" style={{ '--i': 6 }}>click</span>
                <span className="word accent-word" style={{ '--i': 7 }}>away.</span>
              </span>
            </h1>

            <p>
              Discover books, explore new ideas and expand
              your knowledge through our online library.
            </p>

            <div className="hero-chips">
              <span className="hero-chip">PDF books</span>
              <span className="hero-chip">Video tutorials</span>
              <span className="hero-chip">Free membership</span>
            </div>

            <div className="hero-actions">
              <a href="#catalogue" className="primary-button">
                Explore Books →
              </a>

              <button
                type="button"
                className="secondary-button"
                onClick={() =>
                  currentUser
                    ? setCurrentPage('shelf')
                    : setCurrentPage('register')
                }
              >
                {currentUser ? 'Open my shelf' : 'Create free account'}
              </button>
            </div>

            <p className="hero-note">
              No card required · Built for students on the move.
            </p>

          </div>

          <div className="hero-visual reveal">

            <div className="hero-card">

              <span className="hero-card-label">
                YOUR NEXT CHAPTER
              </span>

              <div className="hero-book">
                <span>READ</span>
                <strong>LEARN.</strong>
                <span>GROW.</span>
              </div>

              <p>
                Knowledge is always within reach.
              </p>

              <div className="hero-card-stats">
                <div>
                  <strong>{stats ? stats.books : '—'}</strong>
                  <span>books</span>
                </div>
                <div>
                  <strong>{stats ? stats.videos : '—'}</strong>
                  <span>videos</span>
                </div>
              </div>

            </div>

            <div className="hero-float-card" aria-hidden="true">
              <span className="hero-float-dot" />
              <div>
                <strong>Always open</strong>
                <span>24 hours a day</span>
              </div>
            </div>

          </div>
        </section>

        {/* Library statistics */}
        <section className="stats-band reveal" aria-label="Library statistics">

          <div className="stats-item">
            <strong>
              <AnimatedCounter value={stats ? stats.resources : 0} />
            </strong>
            <span>Curated resources</span>
          </div>

          <div className="stats-item">
            <strong>
              <AnimatedCounter value={stats ? stats.books : 0} />
            </strong>
            <span>Books to read</span>
          </div>

          <div className="stats-item">
            <strong>
              <AnimatedCounter value={stats ? stats.videos : 0} />
            </strong>
            <span>Video tutorials</span>
          </div>

          <div className="stats-item">
            <strong>
              <AnimatedCounter value={stats ? stats.categories : 0} />
            </strong>
            <span>Topic categories</span>
          </div>

        </section>

        {/* Categories */}
        <section className="section" id="categories">

          <div className="section-heading reveal">
            <div>
              <span className="eyebrow">DISCOVER</span>

              <h2>Explore Categories</h2>

              <p>
                Find learning materials that interest you.
              </p>
            </div>
          </div>

          <div className="category-list reveal">

            <button
              className={
                activeCategory === ''
                  ? 'category-button active'
                  : 'category-button'
              }
              style={{ '--i': 0 }}
              onClick={() => setActiveCategory('')}
            >
              All
            </button>

            {categories.map((category, index) => (
              <button
                key={category.id}
                className={
                  activeCategory === String(category.id)
                    ? 'category-button active'
                    : 'category-button'
                }
                style={{ '--i': index + 1 }}
                onClick={() =>
                  setActiveCategory(String(category.id))
                }
              >
                {category.name}
              </button>
            ))}

          </div>
        </section>

        {/* Book catalogue */}
        <section
          className="section catalogue"
          id="catalogue"
        >

          <div className="section-heading reveal">
            <div>
              <span className="eyebrow">
                OUR COLLECTION
              </span>

              <h2>Explore Our Library</h2>

              <p>
                Discover books and video tutorials.
              </p>
            </div>

            {!loading && !error && (
              <span className="result-count">
                {totalResources}{' '}
                {totalResources === 1 ? 'result' : 'results'}
              </span>
            )}
          </div>

          {/* Search */}
          <div className="search-wrap">

            <svg
              className="search-icon"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle
                cx="10.5"
                cy="10.5"
                r="6.5"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
              />
              <path
                d="m15.6 15.6 4.4 4.4"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
              />
            </svg>

            <input
              ref={searchRef}
              type="text"
              className="search-input"
              placeholder="Search by title, author or publisher..."
              value={search}
              onChange={(event) =>
                setSearch(event.target.value)
              }
              aria-label="Search the library"
            />

            {search ? (
              <button
                type="button"
                className="search-clear"
                onClick={() => setSearch('')}
                aria-label="Clear search"
              >
                ×
              </button>
            ) : (
              <kbd className="search-key" aria-hidden="true">/</kbd>
            )}

          </div>

          {/* Resource type filter */}
          <div className="type-filter">

            {[
              { value: '', label: 'All' },
              { value: 'book', label: 'Books' },
              { value: 'video', label: 'Videos' }
            ].map((type) => (
              <button
                key={type.value || 'all'}
                type="button"
                className={
                  resourceType === type.value
                    ? 'type-button active'
                    : 'type-button'
                }
                onClick={() => setResourceType(type.value)}
              >
                {type.label}
              </button>
            ))}

          </div>

          {/* Loading skeletons */}
          {loading && (
            <div className="book-grid" aria-hidden="true">
              {[0, 1, 2, 3, 4, 5].map((item) => (
                <div className="skeleton-card" key={item}>
                  <div className="skeleton-cover" />
                  <div className="skeleton-line" />
                  <div className="skeleton-line short" />
                  <div className="skeleton-line tiny" />
                </div>
              ))}
            </div>
          )}

          {/* Error state */}
          {!loading && error && (
            <p className="error-message" role="alert">
              {error}
            </p>
          )}

          {/* Resources */}
          {!loading && !error && resources.length > 0 && (
            <div className="book-grid">

              {resources.map((resource, index) => (
                <ResourceCard
                  key={resource.id}
                  resource={resource}
                  index={index}
                  isFavorite={favoriteIds.has(resource.id)}
                  onOpen={setSelectedResource}
                  onFavorite={toggleFavorite}
                />
              ))}

            </div>
          )}

          {/* Load further batches only on request */}
          {!loading && !error && resources.length > 0 && (
            <div className="catalogue-more">

              <p className="catalogue-progress">
                Showing {resources.length} of {totalResources}
              </p>

              {hasMore && (
                <div className="catalogue-more-actions">
                  <button
                    type="button"
                    className="secondary-button"
                    disabled={loadingMore}
                    onClick={() => loadMore(false)}
                  >
                    {loadingMore ? 'Loading...' : 'Show more'}
                  </button>

                  <button
                    type="button"
                    className="primary-button"
                    disabled={loadingMore}
                    onClick={() => loadMore(true)}
                  >
                    Show all {totalResources}
                  </button>
                </div>
              )}

              {!hasMore && resources.length > PAGE_SIZE && (
                <button
                  type="button"
                  className="secondary-button"
                  onClick={showLess}
                >
                  Show less
                </button>
              )}

            </div>
          )}
          {!loading && !error && resources.length === 0 && (
            <div className="empty-state reveal">

              <span className="empty-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24">
                  <circle
                    cx="10.5"
                    cy="10.5"
                    r="6.5"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                  />
                  <path
                    d="m15.6 15.6 4.4 4.4"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                  />
                </svg>
              </span>

              <h3>No matches yet</h3>

              <p>
                Try another title, author or category.
              </p>

              {hasFilters && (
                <button
                  type="button"
                  className="secondary-button"
                  onClick={resetFilters}
                >
                  Clear filters
                </button>
              )}

            </div>
          )}

        </section>

        {/* About */}
        <section className="about-section" id="about">

          <span className="eyebrow">
            ABOUT OUR LIBRARY
          </span>

          <h2>Learning made accessible.</h2>

          <p>
            E-Library is an online library management system
            designed to help users discover, access and read
            educational resources conveniently.
          </p>

          {/* General library information */}
          <div className="library-info-grid">

            <div className="info-card reveal">
              <h3>Opening Hours</h3>
              <p>Monday – Friday: 8:00 AM – 8:00 PM</p>
              <p>Saturday: 9:00 AM – 5:00 PM</p>
              <p>Sunday: Closed</p>
            </div>

            <div className="info-card reveal">
              <h3>Location</h3>
              <p>E-Library Learning Centre</p>
              <p>Main Campus, Library Block</p>
            </div>

            <div className="info-card reveal">
              <h3>Membership</h3>
              <p>Free registration for all students.</p>
              <p>Log in to read, watch and download.</p>
            </div>

            <div className="info-card reveal">
              <h3>Need Help?</h3>
              <p>Send us a message through the contact page.</p>
              <p>Or ask the librarian on duty.</p>
            </div>

          </div>

        </section>

      </main>

      {/* Footer */}
      <footer className="footer">

        <div className="footer-grid">

          <div>
            <h3>E-Library</h3>

            <p>Discover. Read. Learn. Grow.</p>

            <p>
              Your digital learning space, open around the clock.
            </p>
          </div>

          <div>
            <h4>Explore</h4>

            <a href="#catalogue" className="footer-link">Books</a>
            <a href="#categories" className="footer-link">Categories</a>
            <a href="#about" className="footer-link">About</a>
          </div>

          <div>
            <h4>Support</h4>

            <button
              type="button"
              className="footer-link"
              onClick={() => setCurrentPage('contact')}
            >
              Contact us
            </button>

            <a href="#home" className="footer-link">Back to top</a>
          </div>

        </div>

        <p className="footer-bottom">
          © 2026 E-Library Management System.
        </p>

      </footer>

      {/* Resource detail modal */}
      {selectedResource && (
        <ResourceModal
          resource={selectedResource}
          currentUser={currentUser}
          isFavorite={favoriteIds.has(selectedResource.id)}
          onFavorite={toggleFavorite}
          isBorrowed={Boolean(activeLoanFor(selectedResource.id))}
          borrowedLoan={activeLoanFor(selectedResource.id)}
          onBorrow={borrowResource}
          onClose={() => setSelectedResource(null)}
        />
      )}

      <Toast toast={toast} />

      {scrolled && (
        <button
          type="button"
          className="to-top"
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          aria-label="Back to top"
        >
          ↑
        </button>
      )}

    </div>
  );
}

export default App;
