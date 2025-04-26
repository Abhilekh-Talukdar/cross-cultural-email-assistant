import React, { useState } from 'react';
import axios from 'axios';
import styles from './App.module.css'; // Import the CSS module

// Define available cultures and tones (should match backend)
const CULTURES = ["Japan", "U.S.", "U.K.", "France", "India", "Germany"];
const TONES = ["Clarity", "Formality", "Urgency", "Respect"];

function App() {
  // --- State Variables (remain the same) ---
  const [originalSubject, setOriginalSubject] = useState('');
  const [originalBody, setOriginalBody] = useState('');
  const [targetCulture, setTargetCulture] = useState(CULTURES[0]);
  const [toneEmphasis, setToneEmphasis] = useState<string | null>(null);
  const [rewrittenSubject, setRewrittenSubject] = useState('');
  const [rewrittenBody, setRewrittenBody] = useState('');
  const [culturalNotes, setCulturalNotes] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // --- Handle Rewrite Action (remains the same) ---
  const handleRewrite = async () => {
    setIsLoading(true);
    setError(null);
    setRewrittenSubject('');
    setRewrittenBody('');
    setCulturalNotes('');

    try {
      const response = await axios.post('http://localhost:8000/rewrite', { // Ensure backend URL is correct
        subject: originalSubject,
        body: originalBody,
        target_culture: targetCulture,
        tone_emphasis: toneEmphasis || undefined,
      });

      if (response.data) {
        setRewrittenSubject(response.data.rewritten_subject);
        setRewrittenBody(response.data.rewritten_body);
        setCulturalNotes(response.data.cultural_notes);
      }
    } catch (err: any) {
       console.error("Rewrite error:", err);
       if (err.response && err.response.data && err.response.data.detail) {
           setError(`Error: ${err.response.data.detail}`);
       } else if (err.request) {
           setError('Error: Could not reach the backend server. Is it running?');
       } else {
           setError(`An unexpected error occurred: ${err.message}`);
       }
    } finally {
      setIsLoading(false);
    }
  };

  // --- JSX Structure using CSS Modules ---
  return (
    <div className={styles.container}>
      <h1 className={styles.title}>
        Cross-Cultural Email Assistant
      </h1>

      <div className={styles.gridContainer}>
        {/* --- Input Section --- */}
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>Original Email</h2>

          <div /* className="mb-4" - margins handled by elements below */ >
            <label htmlFor="subject" className={styles.formLabel}>
              Subject:
            </label>
            <input
              type="text"
              id="subject"
              value={originalSubject}
              onChange={(e) => setOriginalSubject(e.target.value)}
              className={styles.formInput}
              placeholder="Enter email subject"
            />
          </div>

          <div>
            <label htmlFor="body" className={styles.formLabel}>
              Body:
            </label>
            <textarea
              id="body"
              rows={10} // You can keep rows attribute or rely purely on CSS height
              value={originalBody}
              onChange={(e) => setOriginalBody(e.target.value)}
              className={styles.formTextarea}
              placeholder="Enter email body..."
            />
          </div>

          <div>
            <label htmlFor="culture" className={styles.formLabel}>
              Target Culture:
            </label>
            <select
              id="culture"
              value={targetCulture}
              onChange={(e) => setTargetCulture(e.target.value)}
              className={styles.formSelect}
            >
              {CULTURES.map((culture) => (
                <option key={culture} value={culture}>
                  {culture}
                </option>
              ))}
            </select>
          </div>

           <div>
            <label htmlFor="tone" className={styles.formLabel}>
              Optional Tone Emphasis:
            </label>
            <select
              id="tone"
              value={toneEmphasis ?? ''}
              onChange={(e) => setToneEmphasis(e.target.value || null)}
              className={styles.formSelect}
            >
               <option value="">-- None --</option>
               {TONES.map((tone) => (
                <option key={tone} value={tone}>
                  {tone}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleRewrite}
            disabled={isLoading || !originalBody.trim()}
            className={styles.submitButton}
          >
            {isLoading ? 'Rewriting...' : 'Rewrite Email'}
          </button>
           {error && (
              <p className={styles.errorMessage}>{error}</p>
           )}
        </div>

        {/* --- Output Section --- */}
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>Rewritten Email & Notes</h2>

          {isLoading && (
             <p className={styles.loadingMessage}>Loading results...</p>
          )}

           {!isLoading && (rewrittenSubject || rewrittenBody || culturalNotes) && (
             <>
               <div>
                 <h3 className={styles.outputSectionTitle}>Rewritten Subject:</h3>
                 <div className={styles.outputBox}>
                   {rewrittenSubject || '(No subject rewritten)'}
                 </div>
               </div>

               <div>
                 <h3 className={styles.outputSectionTitle}>Rewritten Body:</h3>
                 <div className={`${styles.outputBox} ${styles.outputBodyBox}`}>
                   {rewrittenBody || '(No body rewritten)'}
                 </div>
               </div>

               <div>
                 <h3 className={styles.outputSectionTitle}>Cultural Notes:</h3>
                 <div className={styles.notesBox}>
                   {culturalNotes || '(No cultural notes provided)'}
                 </div>
               </div>
             </>
           )}
            {!isLoading && !error && !rewrittenBody && !culturalNotes && (
                 <p className={styles.placeholderMessage}>Enter an email and click "Rewrite" to see the results here.</p>
            )}
        </div>
      </div>
    </div>
  );
}

export default App;