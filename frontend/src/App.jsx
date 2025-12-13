// frontend/src/App.jsx - Minimalist Design with Loading States
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/clerk-react";
import { useUser } from "@clerk/clerk-react";
import { useState, useEffect } from "react";
import axios from "axios";

axios.defaults.baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function Dashboard() {
  const { user } = useUser();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [analyzingProducts, setAnalyzingProducts] = useState(new Set());

  // Form state
  const [name, setName] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [links, setLinks] = useState([{ platform: "amazon", url: "" }]);

  const loadProducts = async () => {
    try {
      const token = await window.Clerk.session.getToken({ template: "fastapi" });
      const res = await axios.get("/api/products", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setProducts(res.data);
      
      // Check which products have completed analysis
      const newAnalyzingSet = new Set(analyzingProducts);
      res.data.forEach(product => {
        const link = product.links[0];
        if (link?.last_scraped || link?.fake_ratio !== null) {
          // Analysis is complete, remove from analyzing set
          newAnalyzingSet.delete(product.id);
        }
      });
      setAnalyzingProducts(newAnalyzingSet);
      
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
    const interval = setInterval(loadProducts, 10000);
    return () => clearInterval(interval);
  }, []);

  const addLinkField = () => {
    setLinks([...links, { platform: "amazon", url: "" }]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const nonAmazonLinks = links.filter(l => l.url.trim() && !l.url.toLowerCase().includes("amazon"));
    if (nonAmazonLinks.length > 0) {
      alert("Only Amazon product links are supported!");
      return;
    }

    try {
      const token = await window.Clerk.session.getToken({ template: "fastapi" });
      const response = await axios.post(
        "/api/products",
        {
          name,
          image_url: imageUrl || null,
          links: links.filter(l => l.url.trim() !== ""),
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Mark this product as analyzing
      setAnalyzingProducts(prev => new Set([...prev, response.data.id]));

      setName("");
      setImageUrl("");
      setLinks([{ platform: "amazon", url: "" }]);
      setShowForm(false);
      await loadProducts();
    } catch (err) {
      alert("Error: " + (err.response?.data?.detail || err.message));
    }
  };

  const handleScrape = async (productId) => {
    setAnalyzingProducts(prev => new Set([...prev, productId]));
    try {
      const token = await window.Clerk.session.getToken({ template: "fastapi" });
      await axios.post(
        `/api/products/${productId}/scrape`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // The loadProducts interval will automatically clear the analyzing state
    } catch (err) {
      alert("Error: " + (err.response?.data?.detail || err.message));
      setAnalyzingProducts(prev => {
        const newSet = new Set(prev);
        newSet.delete(productId);
        return newSet;
      });
    }
  };

  const handleDelete = async (productId) => {
    if (!confirm("Delete this product?")) return;
    
    try {
      const token = await window.Clerk.session.getToken({ template: "fastapi" });
      await axios.delete(`/api/products/${productId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      await loadProducts();
      setSelectedProduct(null);
    } catch (err) {
      alert("Error: " + (err.response?.data?.detail || err.message));
    }
  };

  // Check if product is being analyzed
  const isAnalyzing = (product) => {
    const link = product.links[0];
    // Check if in analyzing set OR if never scraped AND not in error state
    return analyzingProducts.has(product.id) || 
           (!link?.last_scraped && !link?.scrape_note?.includes("Error"));
  };

  const getStatusInfo = (link) => {
    if (!link.last_scraped) {
      return { text: "Analyzing", color: "text-gray-600", bg: "bg-gray-100" };
    }
    if (link.fake_ratio === null) {
      return { text: "Processing", color: "text-gray-600", bg: "bg-gray-100" };
    }
    if (link.fake_ratio > 0.5) {
      return { text: "High Risk", color: "text-red-600", bg: "bg-red-50" };
    }
    if (link.fake_ratio > 0.3) {
      return { text: "Moderate Risk", color: "text-orange-600", bg: "bg-orange-50" };
    }
    return { text: "Trustworthy", color: "text-green-600", bg: "bg-green-50" };
  };

  const getSentimentInfo = (score) => {
    if (score === null || score === undefined) return { text: "—", color: "text-gray-400" };
    if (score > 0.3) return { text: "Positive", color: "text-green-600" };
    if (score > -0.3) return { text: "Mixed", color: "text-gray-600" };
    return { text: "Negative", color: "text-red-600" };
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header */}
        <div className="flex justify-between items-center mb-12">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {user?.firstName ? `Hello, ${user.firstName}` : 'RepuTrack'}
            </h1>
            <p className="text-gray-500 mt-1">AI-powered review analysis</p>
          </div>
          <UserButton />
        </div>

        {/* Actions Bar */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-900">
            Products ({products.length})
          </h2>
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-5 py-2.5 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 transition"
          >
            {showForm ? "Cancel" : "+ Add Product"}
          </button>
        </div>

        {/* ADD FORM */}
        {showForm && (
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8">
            <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <p className="text-sm text-gray-700">
                <strong>Note:</strong> Only Amazon links are supported. Analysis takes 1-2 minutes.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Product Name *
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                  placeholder="e.g. Boat Airdopes 161"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Image URL (optional)
                </label>
                <input
                  type="url"
                  value={imageUrl}
                  onChange={(e) => setImageUrl(e.target.value)}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                  placeholder="https://..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Amazon Product Link *
                </label>
                {links.map((link, i) => (
                  <div key={i} className="flex gap-3 mb-3">
                    <input
                      type="url"
                      required
                      value={link.url}
                      onChange={(e) => {
                        const newLinks = [...links];
                        newLinks[i].url = e.target.value;
                        setLinks(newLinks);
                      }}
                      className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                      placeholder="https://www.amazon.in/dp/..."
                    />
                  </div>
                ))}
              </div>

              <button
                type="submit"
                className="w-full py-3 bg-gray-900 text-white font-medium rounded-lg hover:bg-gray-800 transition"
              >
                Add Product
              </button>
            </form>
          </div>
        )}

        {/* PRODUCTS GRID */}
        {loading ? (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-10 w-10 border-2 border-gray-900 border-t-transparent"></div>
            <p className="text-gray-600 mt-4 text-sm">Loading products...</p>
          </div>
        ) : products.length === 0 && !showForm ? (
          <div className="text-center py-20 bg-white rounded-xl border border-gray-200">
            <div className="text-5xl mb-4">📦</div>
            <p className="text-lg text-gray-900 mb-1">No products yet</p>
            <p className="text-gray-500 text-sm">Add your first product to start tracking</p>
          </div>
        ) : (
          <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {products.map((p) => {
              const link = p.links[0];
              const analyzing = isAnalyzing(p);
              const status = link ? getStatusInfo(link) : null;
              const sentiment = link ? getSentimentInfo(link.sentiment_score) : null;

              return (
                <div 
                  key={p.id} 
                  className="bg-white rounded-xl border border-gray-200 hover:border-gray-300 transition-all cursor-pointer overflow-hidden"
                  onClick={() => !analyzing && setSelectedProduct(p)}
                >
                  {p.image_url && (
                    <div className="h-44 bg-gray-50 border-b border-gray-200">
                      <img 
                        src={p.image_url} 
                        alt={p.name} 
                        className="w-full h-full object-contain p-4" 
                      />
                    </div>
                  )}
                  
                  <div className="p-5">
                    <h3 className="font-semibold text-gray-900 mb-3 line-clamp-2">{p.name}</h3>
                    
                    {analyzing ? (
                      <div className="space-y-3">
                        <div className="flex items-center gap-2 text-gray-600">
                          <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-900 border-t-transparent"></div>
                          <span className="text-sm font-medium">Analyzing reviews...</span>
                        </div>
                        <div className="space-y-2">
                          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div className="h-full bg-gray-900 rounded-full animate-pulse w-3/4"></div>
                          </div>
                          <p className="text-xs text-gray-500">This may take 1-2 minutes</p>
                        </div>
                      </div>
                    ) : link && status ? (
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className={`px-3 py-1.5 rounded-md text-xs font-medium ${status.bg} ${status.color}`}>
                            {status.text}
                          </span>
                          {link.last_rating && (
                            <span className="text-sm font-semibold text-gray-900">
                              ⭐ {link.last_rating.toFixed(1)}
                            </span>
                          )}
                        </div>
                        
                        {link.fake_ratio !== null && (
                          <div>
                            <div className="flex justify-between text-xs mb-1.5">
                              <span className="text-gray-600">Fake Detection</span>
                              <span className="font-semibold text-gray-900">{(link.fake_ratio * 100).toFixed(0)}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-1.5">
                              <div 
                                className={`h-1.5 rounded-full ${
                                  link.fake_ratio > 0.5 ? 'bg-red-600' : 
                                  link.fake_ratio > 0.3 ? 'bg-orange-600' : 
                                  'bg-green-600'
                                }`}
                                style={{ width: `${link.fake_ratio * 100}%` }}
                              ></div>
                            </div>
                          </div>
                        )}
                        
                        {sentiment && link.sentiment_score !== null && (
                          <div className="flex items-center justify-between py-2 border-t border-gray-100">
                            <span className="text-xs text-gray-600">Sentiment</span>
                            <span className={`text-sm font-semibold ${sentiment.color}`}>
                              {sentiment.text}
                            </span>
                          </div>
                        )}
                        
                        {link.last_scraped && (
                          <p className="text-xs text-gray-400 pt-2 border-t border-gray-100">
                            Updated {new Date(link.last_scraped).toLocaleDateString()}
                          </p>
                        )}
                      </div>
                    ) : null}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* DETAIL MODAL */}
      {selectedProduct && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedProduct(null)}
        >
          <div 
            className="bg-white rounded-2xl shadow-xl max-w-3xl w-full max-h-[85vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="sticky top-0 bg-white border-b border-gray-200 p-6 rounded-t-2xl">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-1">{selectedProduct.name}</h2>
                  <p className="text-sm text-gray-500">Analysis Overview</p>
                </div>
                <button 
                  onClick={() => setSelectedProduct(null)}
                  className="text-gray-400 hover:text-gray-600 text-2xl w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100"
                >
                  ×
                </button>
              </div>
            </div>

            <div className="p-6">
              {selectedProduct.image_url && (
                <div className="mb-6 bg-gray-50 rounded-xl p-6 border border-gray-200">
                  <img 
                    src={selectedProduct.image_url} 
                    alt={selectedProduct.name}
                    className="w-full max-h-64 object-contain"
                  />
                </div>
              )}

              {selectedProduct.links.map((link) => {
                const analyzing = isAnalyzing(selectedProduct);
                const status = getStatusInfo(link);
                const sentiment = getSentimentInfo(link.sentiment_score);

                return (
                  <div key={link.id}>
                    <div className="flex flex-wrap items-center justify-between gap-4 mb-6 pb-4 border-b border-gray-200">
                      <div className="flex items-center gap-3">
                        <span className="px-3 py-1.5 bg-gray-900 text-white text-sm font-semibold rounded-lg">
                          Amazon
                        </span>
                        {link.last_rating && (
                          <span className="text-xl font-bold text-gray-900">
                            ⭐ {link.last_rating.toFixed(1)}
                          </span>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleScrape(selectedProduct.id)}
                          disabled={analyzingProducts.has(selectedProduct.id)}
                          className="px-4 py-2 bg-gray-100 text-gray-900 rounded-lg hover:bg-gray-200 transition disabled:opacity-50 text-sm font-medium"
                        >
                          {analyzingProducts.has(selectedProduct.id) ? "Refreshing..." : "Refresh"}
                        </button>
                        <a
                          href={link.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition text-sm font-medium"
                        >
                          View on Amazon
                        </a>
                      </div>
                    </div>

                    {analyzing ? (
                      <div className="py-12 text-center">
                        <div className="inline-block animate-spin rounded-full h-12 w-12 border-3 border-gray-900 border-t-transparent mb-4"></div>
                        <p className="text-gray-900 font-medium mb-2">Analyzing reviews...</p>
                        <p className="text-sm text-gray-500">This may take 1-2 minutes. We'll update automatically.</p>
                      </div>
                    ) : link.fake_ratio !== null ? (
                      <div className="space-y-6">
                        <div className="grid md:grid-cols-3 gap-4">
                          <div className={`p-5 rounded-xl border-2 ${status.bg} border-gray-200`}>
                            <p className="text-xs font-medium text-gray-600 mb-1">Status</p>
                            <p className={`text-xl font-bold ${status.color}`}>{status.text}</p>
                          </div>
                          
                          <div className="p-5 rounded-xl bg-gray-50 border-2 border-gray-200">
                            <p className="text-xs font-medium text-gray-600 mb-1">Fake Reviews</p>
                            <p className="text-xl font-bold text-gray-900">{(link.fake_ratio * 100).toFixed(0)}%</p>
                          </div>
                          
                          <div className="p-5 rounded-xl bg-gray-50 border-2 border-gray-200">
                            <p className="text-xs font-medium text-gray-600 mb-1">Sentiment</p>
                            <p className={`text-xl font-bold ${sentiment.color}`}>{sentiment.text}</p>
                          </div>
                        </div>

                        {link.last_scraped && (
                          <p className="text-xs text-gray-500 text-center pt-4 border-t border-gray-200">
                            Last analyzed on {new Date(link.last_scraped).toLocaleDateString('en-US', { 
                              year: 'numeric', 
                              month: 'long', 
                              day: 'numeric' 
                            })}
                          </p>
                        )}
                      </div>
                    ) : (
                      <div className="py-12 text-center bg-gray-50 rounded-xl border border-gray-200">
                        <p className="text-gray-600">
                          {link.scrape_note || "No analysis data available"}
                        </p>
                      </div>
                    )}
                  </div>
                );
              })}

              <div className="flex gap-3 pt-6 border-t border-gray-200 mt-6">
                <button
                  onClick={() => handleDelete(selectedProduct.id)}
                  className="flex-1 px-4 py-2.5 bg-red-50 text-red-600 rounded-lg font-medium hover:bg-red-100 transition border border-red-200"
                >
                  Delete Product
                </button>
                <button
                  onClick={() => setSelectedProduct(null)}
                  className="flex-1 px-4 py-2.5 bg-gray-100 text-gray-900 rounded-lg font-medium hover:bg-gray-200 transition"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function App() {
  return (
    <>
      <SignedIn>
        <Dashboard />
      </SignedIn>
      <SignedOut>
        <div className="min-h-screen bg-white flex items-center justify-center px-6">
          <div className="text-center max-w-2xl">
            <h1 className="text-6xl font-bold text-gray-900 mb-4">RepuTrack</h1>
            <p className="text-xl text-gray-600 mb-12">
              AI-powered Amazon review analysis. Detect fake reviews instantly.
            </p>
            <SignInButton mode="modal">
              <button className="px-10 py-4 bg-gray-900 text-white text-lg font-semibold rounded-xl hover:bg-gray-800 transition">
                Sign in to Continue
              </button>
            </SignInButton>
          </div>
        </div>
      </SignedOut>
    </>
  );
}