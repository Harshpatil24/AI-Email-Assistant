export default function EmailCard({ email }) {
  const { record, classification, draft } = email;

  return (
    <div className="bg-white shadow-md rounded-2xl p-4 space-y-3">
      <h2 className="font-bold text-lg">{record.subject}</h2>
      <p className="text-sm text-gray-600">From: {record.sender}</p>
      <p className="text-gray-700">{record.snippet}</p>

      {classification && (
        <div className="bg-gray-50 p-3 rounded-md">
          <p><strong>Summary:</strong> {classification.summary}</p>
          <p><strong>Category:</strong> {classification.category}</p>
          <p><strong>Sentiment:</strong> {classification.sentiment}</p>
          <p><strong>Priority:</strong> {classification.priority}</p>
        </div>
      )}

      {draft && (
        <div className="bg-blue-50 p-3 rounded-md">
          <h3 className="font-semibold">Suggested Reply</h3>
          <p className="text-sm text-gray-700 whitespace-pre-line">{draft.body}</p>
          <div className="mt-2 flex gap-2">
            <button className="bg-green-500 text-white px-3 py-1 rounded">Approve</button>
            <button className="bg-red-500 text-white px-3 py-1 rounded">Reject</button>
          </div>
        </div>
      )}
    </div>
  );
}
