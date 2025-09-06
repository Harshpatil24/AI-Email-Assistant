import { useEffect, useState } from "react";
import EmailCard from "../components/EmailCard";

export default function Dashboard() {
  const [emails, setEmails] = useState([]);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_BACKEND_URL}/emails`)
      .then(res => res.json())
      .then(data => setEmails(data))
      .catch(err => console.error("Error fetching:", err));
  }, []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {emails.length === 0 ? (
        <p className="text-gray-600">No emails processed yet.</p>
      ) : (
        emails.map((item, idx) => (
          <EmailCard key={idx} email={item} />
        ))
      )}
    </div>
  );
}
