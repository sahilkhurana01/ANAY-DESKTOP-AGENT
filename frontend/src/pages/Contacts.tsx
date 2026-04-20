import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { UserPlus, Search, Phone, Mail, Users } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

interface Contact {
  id: string;
  name: string;
  phone?: string;
  email?: string;
  notes?: string;
  lastContact?: Date;
}

const Contacts = () => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const [newContact, setNewContact] = useState({ name: '', phone: '', email: '' });

  // Load contacts from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('anay_contacts');
    if (saved) {
      try {
        setContacts(JSON.parse(saved));
      } catch (e) {
        console.error('Error loading contacts:', e);
      }
    }
  }, []);

  // Save contacts to localStorage
  useEffect(() => {
    if (contacts.length > 0) {
      localStorage.setItem('anay_contacts', JSON.stringify(contacts));
    }
  }, [contacts]);

  const filteredContacts = contacts.filter(contact =>
    contact.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    contact.phone?.includes(searchQuery) ||
    contact.email?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleAddContact = () => {
    if (newContact.name.trim()) {
      const contact: Contact = {
        id: Date.now().toString(),
        name: newContact.name,
        phone: newContact.phone || undefined,
        email: newContact.email || undefined,
        lastContact: new Date(),
      };
      setContacts([...contacts, contact]);
      setNewContact({ name: '', phone: '', email: '' });
      setIsAdding(false);
    }
  };

  const handleDeleteContact = (id: string) => {
    setContacts(contacts.filter(c => c.id !== id));
  };

  return (
    <div className="h-full flex flex-col gap-4 p-4">
      <Link to="/" className="text-xs font-orbitron text-muted-foreground hover:text-primary w-fit">
        ← Back to ANAY
      </Link>
      <div className="anay-panel p-4 flex flex-col gap-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-primary" />
            <h2 className="font-orbitron text-primary text-lg tracking-wider anay-glow-text">
              CONTACTS
            </h2>
          </div>
          <Button
            onClick={() => setIsAdding(!isAdding)}
            className="anay-button-secondary"
          >
            <UserPlus className="w-4 h-4 mr-2" />
            Add Contact
          </Button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search contacts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Add Contact Form */}
        {isAdding && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="p-4 bg-secondary/30 rounded-lg space-y-3"
          >
            <Input
              placeholder="Name *"
              value={newContact.name}
              onChange={(e) => setNewContact({ ...newContact, name: e.target.value })}
            />
            <Input
              placeholder="Phone"
              value={newContact.phone}
              onChange={(e) => setNewContact({ ...newContact, phone: e.target.value })}
            />
            <Input
              placeholder="Email"
              type="email"
              value={newContact.email}
              onChange={(e) => setNewContact({ ...newContact, email: e.target.value })}
            />
            <div className="flex gap-2">
              <Button onClick={handleAddContact} className="flex-1">
                Add
              </Button>
              <Button
                onClick={() => {
                  setIsAdding(false);
                  setNewContact({ name: '', phone: '', email: '' });
                }}
                variant="outline"
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </motion.div>
        )}
      </div>

      {/* Contacts List */}
      <div className="flex-1 anay-panel overflow-hidden flex flex-col">
        <div className="p-4 border-b border-border/30">
          <span className="text-xs text-muted-foreground font-orbitron">
            {filteredContacts.length} CONTACT{filteredContacts.length !== 1 ? 'S' : ''}
          </span>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {filteredContacts.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              <Users className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>No contacts found</p>
              {contacts.length === 0 && (
                <p className="text-xs mt-1">Add your first contact to get started</p>
              )}
            </div>
          ) : (
            filteredContacts.map((contact, index) => (
              <motion.div
                key={contact.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="bg-secondary/30 rounded-lg p-4 hover:bg-secondary/50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-orbitron text-foreground mb-2">{contact.name}</h3>
                    <div className="space-y-1 text-sm text-muted-foreground">
                      {contact.phone && (
                        <div className="flex items-center gap-2">
                          <Phone className="w-3 h-3" />
                          <span>{contact.phone}</span>
                        </div>
                      )}
                      {contact.email && (
                        <div className="flex items-center gap-2">
                          <Mail className="w-3 h-3" />
                          <span>{contact.email}</span>
                        </div>
                      )}
                    </div>
                  </div>
                  <Button
                    onClick={() => handleDeleteContact(contact.id)}
                    variant="ghost"
                    size="sm"
                    className="text-destructive hover:text-destructive"
                  >
                    Delete
                  </Button>
                </div>
              </motion.div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Contacts;
