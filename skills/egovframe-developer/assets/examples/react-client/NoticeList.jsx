import { useEffect, useState } from "react";
import { getNotices } from "./egovApi";

export function NoticeList() {
  const [notices, setNotices] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getNotices()
      .then(setNotices)
      .catch((reason) => setError(reason.message));
  }, []);

  if (error) {
    return <p role="alert">{error}</p>;
  }

  return (
    <section>
      <h1>공지사항</h1>
      <ul>
        {notices.map((notice) => (
          <li key={notice.noticeId}>{notice.title}</li>
        ))}
      </ul>
    </section>
  );
}
