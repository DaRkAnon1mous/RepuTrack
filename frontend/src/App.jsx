// frontend/src/App.jsx
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/clerk-react";
import { useUser } from "@clerk/clerk-react";
import { useState, useEffect } from "react";
import axios from "axios";

axios.defaults.baseURL = "http://localhost:8000";

function Dashboard() {
  const { user } = useUser();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);

  // Form state
  const [name, setName] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [links, setLinks] = useState([{ platform: "amazon", url: "" }]);

  // Load products
  const loadProducts = async () => {
    try {
      const token = await window.Clerk.session.getToken({ template: "fastapi" });
      const res = await axios.get("/api/products", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setProducts(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, []);

  // Add new link field
  const addLinkField = () => {
    setLinks([...links, { platform: "flipkart", url: "" }]);
  };

  // Submit form
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = await window.Clerk.session.getToken({ template: "fastapi" });
      await axios.post(
        "/api/products",
        {
          name,
          image_url: imageUrl || null,
          links: links.filter(l => l.url.trim() !== ""),
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Reset form & reload
      setName("");
      setImageUrl("");
      setLinks([{ platform: "amazon", url: "" }]);
      setShowForm(false);
      await loadProducts();
    } catch (err) {
      alert("Error adding product: " + (err.response?.data?.detail || err.message));
    }
  };

  // Delete product
  const handleDelete = async (productId) => {
    if (!confirm("Are you sure you want to delete this product?")) return;
    
    try {
      const token = await window.Clerk.session.getToken({ template: "fastapi" });
      await axios.delete(`/api/products/${productId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      await loadProducts();
      setSelectedProduct(null);
    } catch (err) {
      alert("Error deleting product: " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-6 py-12">
        <div className="flex justify-between items-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900">
            Welcome, {user?.firstName || "User"}!
          </h1>
          <UserButton />
        </div>

        <div className="flex justify-between items-center mb-8">
          <h2 className="text-2xl font-semibold text-gray-800">
            Your Tracked Products ({products.length})
          </h2>
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-6 py-3 bg-black text-white rounded-lg font-medium hover:bg-gray-800 transition"
          >
            {showForm ? "Cancel" : "+ Add New Product"}
          </button>
        </div>

        {/* ADD PRODUCT FORM */}
        {showForm && (
          <div className="bg-white p-8 rounded-2xl shadow-lg mb-10">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Product Name *
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent"
                  placeholder="e.g. Boat Airdopes 161"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Product Image URL (optional)
                </label>
                <input
                  type="url"
                  value={imageUrl}
                  onChange={(e) => setImageUrl(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg"
                  placeholder="https://example.com/image.jpg"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Product Links *
                </label>
                {links.map((link, i) => (
                  <div key={i} className="flex gap-3 mb-3">
                    <select
                      value={link.platform}
                      onChange={(e) => {
                        const newLinks = [...links];
                        newLinks[i].platform = e.target.value;
                        setLinks(newLinks);
                      }}
                      className="px-4 py-3 border border-gray-300 rounded-lg"
                    >
                      <option value="amazon">Amazon</option>
                      <option value="flipkart">Flipkart</option>
                      <option value="myntra">Myntra</option>
                      <option value="other">Other</option>
                    </select>
                    <input
                      type="url"
                      required
                      value={link.url}
                      onChange={(e) => {
                        const newLinks = [...links];
                        newLinks[i].url = e.target.value;
                        setLinks(newLinks);
                      }}
                      className="flex-1 px-4 py-3 border border-gray-300 rounded-lg"
                      placeholder="https://..."
                    />
                  </div>
                ))}
                <button
                  type="button"
                  onClick={addLinkField}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  + Add another link
                </button>
              </div>

              <button
                type="submit"
                className="w-full py-4 bg-black text-white text-lg font-medium rounded-lg hover:bg-gray-800 transition"
              >
                Start Tracking This Product
              </button>
            </form>
          </div>
        )}

        {/* PRODUCTS LIST */}
        {loading ? (
          <p className="text-center text-gray-600 py-20">Loading...</p>
        ) : products.length === 0 && !showForm ? (
          <div className="text-center py-20 bg-white rounded-2xl shadow-lg">
            <p className="text-xl text-gray-600">
              No products yet. Click "Add New Product" to begin!
            </p>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2">
            {products.map((p) => (
              <div 
                key={p.id} 
                className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-shadow cursor-pointer"
                onClick={() => setSelectedProduct(p)}
              >
                {p.image_url && (
                  <img 
                    src={p.image_url} 
                    alt={p.name} 
                    className="w-full h-48 object-cover rounded-lg mb-4" 
                  />
                )}
                <h3 className="text-2xl font-semibold text-gray-900">{p.name}</h3>
                <p className="text-gray-600 mt-3">
                  {p.links?.length || 0} platform{(p.links?.length || 0) !== 1 && "s"} monitored
                </p>
                <p className="text-sm text-gray-500 mt-2">Click to view details</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* PRODUCT DETAIL MODAL */}
      {selectedProduct && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-6 z-50"
          onClick={() => setSelectedProduct(null)}
        >
          <div 
            className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-8">
              <div className="flex justify-between items-start mb-6">
                <h2 className="text-3xl font-bold text-gray-900">{selectedProduct.name}</h2>
                <button 
                  onClick={() => setSelectedProduct(null)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>

              {selectedProduct.image_url && (
                <img 
                  src={selectedProduct.image_url} 
                  alt={selectedProduct.name}
                  className="w-full h-64 object-cover rounded-lg mb-6"
                />
              )}

              <div className="mb-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">
                  Tracked Links ({selectedProduct.links?.length || 0})
                </h3>
                <div className="space-y-3">
                  {selectedProduct.links?.map((link) => (
                    <div key={link.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full capitalize">
                          {link.platform}
                        </span>
                        <a 
                          href={link.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 hover:underline text-sm truncate max-w-xs"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {link.url}
                        </a>
                      </div>
                      <a
                        href={link.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-4 py-2 bg-black text-white text-sm rounded-lg hover:bg-gray-800 transition"
                        onClick={(e) => e.stopPropagation()}
                      >
                        Visit →
                      </a>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex gap-4 pt-6 border-t">
                <button
                  onClick={() => handleDelete(selectedProduct.id)}
                  className="flex-1 px-6 py-3 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 transition"
                >
                  Delete Product
                </button>
                <button
                  onClick={() => setSelectedProduct(null)}
                  className="flex-1 px-6 py-3 bg-gray-200 text-gray-800 rounded-lg font-medium hover:bg-gray-300 transition"
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
        <div className="min-h-screen bg-gray-50 flex items-center justify-center px-6">
          <div className="text-center">
            <h1 className="text-6xl font-bold text-gray-900 mb-6">RepuTrack</h1>
            <p className="text-xl text-gray-600 mb-12 max-w-md mx-auto">
              Track reviews, detect fakes, stay ahead.
            </p>
            <SignInButton mode="modal">
              <button className="px-10 py-4 bg-black text-white text-lg font-medium rounded-xl hover:bg-gray-800 transition shadow-lg">
                Sign in with Google
              </button>
            </SignInButton>
          </div>
        </div>
      </SignedOut>
    </>
  );
}