import { useState, useEffect } from "react";
import { Plus, Trash2, User, Phone, Search, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface Contact {
  name: string;
  phone: string;
  updated_at: string;
}

export default function ContactManager() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [newName, setNewName] = useState("");
  const [newPhone, setNewPhone] = useState("");
  const [isAdding, setIsAdding] = useState(false);
  const { toast } = useToast();

  const fetchContacts = async () => {
    try {
      setLoading(true);
      const data = await api.getContacts();
      setContacts(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContacts();
  }, []);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName || !newPhone) return;
    
    // Simple validation: 10-12 digits
    const cleanPhone = newPhone.replace(/\D/g, "");
    if (cleanPhone.length < 10) {
      toast({ title: "Invalid Phone", description: "Please enter at least 10 digits.", variant: "destructive" });
      return;
    }

    try {
      await api.addContact(newName, cleanPhone);
      toast({ title: "Success", description: `${newName} saved to brain.` });
      setNewName("");
      setNewPhone("");
      setIsAdding(false);
      fetchContacts();
    } catch (err) {
      toast({ title: "Error", description: "Failed to save contact.", variant: "destructive" });
    }
  };

  const handleDelete = async (name: string) => {
    try {
      await api.deleteContact(name);
      toast({ title: "Deleted", description: `${name} removed from brain.` });
      fetchContacts();
    } catch (err) {
      toast({ title: "Error", description: "Failed to delete contact.", variant: "destructive" });
    }
  };

  const filtered = contacts.filter(c => 
    c.name.toLowerCase().includes(search.toLowerCase()) || 
    c.phone.includes(search)
  );

  return (
    <div style={{ padding: "20px", color: "white" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <div>
          <h2 style={{ fontSize: "20px", fontWeight: "600", marginBottom: "4px" }}>ANAY Contacts</h2>
          <p style={{ fontSize: "12px", opacity: 0.5 }}>Saved numbers for quick messaging</p>
        </div>
        <button 
          onClick={() => setIsAdding(!isAdding)}
          style={{ 
            background: "white", 
            color: "black", 
            border: "none", 
            padding: "8px 12px", 
            borderRadius: "6px", 
            display: "flex", 
            alignItems: "center", 
            gap: "6px", 
            fontSize: "14px",
            fontWeight: "500",
            cursor: "pointer" 
          }}
        >
          <Plus size={16} />
          {isAdding ? "Close" : "Add Contact"}
        </button>
      </header>

      {isAdding && (
        <form onSubmit={handleAdd} style={{ 
          background: "rgba(255,255,255,0.03)", 
          padding: "16px", 
          borderRadius: "12px", 
          border: "1px solid rgba(255,255,255,0.05)",
          marginBottom: "20px",
          display: "flex",
          flexDirection: "column",
          gap: "12px"
        }}>
          <div style={{ display: "flex", gap: "10px" }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: "block", fontSize: "11px", opacity: 0.5, marginBottom: "4px" }}>NAME</label>
              <input 
                value={newName}
                onChange={e => setNewName(e.target.value)}
                placeholder="Vansh..."
                style={{ width: "100%", background: "rgba(0,0,0,0.2)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "6px", padding: "8px 12px", color: "white" }}
              />
            </div>
            <div style={{ flex: 1 }}>
              <label style={{ display: "block", fontSize: "11px", opacity: 0.5, marginBottom: "4px" }}>PHONE (WITH COUNTRY CODE)</label>
              <input 
                value={newPhone}
                onChange={e => setNewPhone(e.target.value)}
                placeholder="919876543210"
                style={{ width: "100%", background: "rgba(0,0,0,0.2)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "6px", padding: "8px 12px", color: "white" }}
              />
            </div>
          </div>
          <button type="submit" style={{ background: "#e53935", color: "white", border: "none", padding: "10px", borderRadius: "6px", fontWeight: "600", cursor: "pointer" }}>
            Save Contact
          </button>
        </form>
      )}

      <div style={{ position: "relative", marginBottom: "16px" }}>
        <Search size={14} style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", opacity: 0.3 }} />
        <input 
          placeholder="Search contacts..." 
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ width: "100%", background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.05)", borderRadius: "8px", padding: "10px 10px 10px 36px", fontSize: "14px", color: "white" }}
        />
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        {loading ? (
          <div style={{ display: "flex", justifyContent: "center", padding: "40px" }}><Loader2 className="animate-spin" style={{ opacity: 0.5 }} /></div>
        ) : filtered.length === 0 ? (
          <div style={{ textAlign: "center", padding: "40px", opacity: 0.3, fontSize: "14px" }}>No contacts found.</div>
        ) : filtered.map(contact => (
          <div key={contact.name} style={{ 
            display: "flex", 
            alignItems: "center", 
            padding: "12px", 
            background: "rgba(255,255,255,0.02)", 
            borderRadius: "10px",
            border: "1px solid rgba(255,255,255,0.03)",
            justifyContent: "space-between"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <div style={{ width: "36px", height: "36px", borderRadius: "50%", background: "rgba(229,57,53,0.1)", color: "#e53935", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: "600" }}>
                {contact.name.charAt(0).toUpperCase()}
              </div>
              <div>
                <div style={{ fontWeight: "600", fontSize: "14px" }}>{contact.name.charAt(0).toUpperCase() + contact.name.slice(1)}</div>
                <div style={{ fontSize: "12px", opacity: 0.5, display: "flex", alignItems: "center", gap: "4px" }}>
                  <Phone size={10} /> {contact.phone}
                </div>
              </div>
            </div>
            <button 
              onClick={() => handleDelete(contact.name)}
              style={{ background: "none", border: "none", color: "rgba(255,255,255,0.2)", cursor: "pointer", padding: "8px" }}
              onMouseEnter={e => e.currentTarget.style.color = "#ef4444"}
              onMouseLeave={e => e.currentTarget.style.color = "rgba(255,255,255,0.2)"}
            >
              <Trash2 size={16} />
            </button>
          </div>
        ))}
      </div>
      
      <p style={{ marginTop: "24px", fontSize: "11px", opacity: 0.3, textAlign: "center" }}>
        ANAY uses this database to send WhatsApp messages by name.
      </p>
    </div>
  );
}
