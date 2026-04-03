import { useMemo, useState } from "react";
import type { ChangeEvent } from "react";
import "./App.css";

type FaceBox = {
  x: number;
  y: number;
  width: number;
  height: number;
};

type UploadResponse = {
  message: string;
  filename: string;
  local_path: string;
  db_result?: unknown;
  faces_detected?: number;
  face_boxes?: FaceBox[];
};

const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"];

export default function App() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [status, setStatus] = useState("Idle");
  const [results, setResults] = useState<UploadResponse[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const totalFilesLabel = useMemo(() => {
    if (selectedFiles.length === 0) return "No files selected";
    if (selectedFiles.length === 1) return "1 file selected";
    return `${selectedFiles.length} files selected`;
  }, [selectedFiles]);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files || []);
    const validFiles = files.filter((file) => ALLOWED_TYPES.includes(file.type));

    if (files.length === 0) {
      setSelectedFiles([]);
      setStatus("Idle");
      return;
    }

    if (validFiles.length !== files.length) {
      setStatus("Some files were skipped. Only JPG, PNG, and WEBP are allowed.");
    } else {
      setStatus("Files ready to upload.");
    }

    setSelectedFiles(validFiles);
  }

  async function handleUpload() {
    if (selectedFiles.length === 0) {
      setStatus("Please select at least one image.");
      return;
    }

    setIsUploading(true);
    setStatus("Uploading and processing...");
    setResults([]);

    try {
      const uploadResults: UploadResponse[] = [];

      for (const file of selectedFiles) {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch("http://127.0.0.1:8000/upload", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Upload failed for ${file.name}: ${errorText}`);
        }

        const data: UploadResponse = await response.json();
        uploadResults.push(data);
      }

      setResults(uploadResults);
      setStatus("Upload complete.");
    } catch (error) {
      console.error(error);
      setStatus(error instanceof Error ? error.message : "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  }

  function clearSelection() {
    setSelectedFiles([]);
    setResults([]);
    setStatus("Idle");
  }

  return (
    <div className="app-shell">
      <div className="background-glow background-glow-one" />
      <div className="background-glow background-glow-two" />

      <main className="app-container">
        <header className="hero-card">
          <div className="hero-copy">
            <p className="eyebrow">Software Capstone Project</p>
            <h1>Celebrity Face Recognition</h1>
            <p className="hero-text">
              Upload one or more images to test the frontend, backend, database,
              and face-detection pipeline.
            </p>
          </div>

          <div className="status-panel">
            <span className={`status-badge ${isUploading ? "uploading" : "idle"}`}>
              {isUploading ? "Processing" : "System Ready"}
            </span>
            <p className="status-label">Current Status</p>
            <p className="status-value">{status}</p>
          </div>
        </header>

        <section className="grid">
          <div className="panel upload-panel">
            <h2>Upload Images</h2>
            <p className="panel-subtext">
              Supported formats: JPG, PNG, WEBP
            </p>

            <label className="dropzone" htmlFor="file-input">
              <div className="dropzone-icon">⬆</div>
              <p className="dropzone-title">Choose image files</p>
              <p className="dropzone-subtitle">
                Select one or multiple files from your computer
              </p>
              <input
                id="file-input"
                type="file"
                multiple
                accept=".jpg,.jpeg,.png,.webp"
                onChange={handleFileChange}
                className="hidden-input"
              />
            </label>

            <div className="selection-summary">
              <span>{totalFilesLabel}</span>
            </div>

            {selectedFiles.length > 0 && (
              <ul className="file-list">
                {selectedFiles.map((file) => (
                  <li key={`${file.name}-${file.size}`} className="file-item">
                    <span className="file-name">{file.name}</span>
                    <span className="file-size">
                      {(file.size / 1024).toFixed(1)} KB
                    </span>
                  </li>
                ))}
              </ul>
            )}

            <div className="button-row">
              <button
                className="primary-button"
                onClick={handleUpload}
                disabled={isUploading}
              >
                {isUploading ? "Uploading..." : "Upload Images"}
              </button>

              <button
                className="secondary-button"
                onClick={clearSelection}
                disabled={isUploading}
              >
                Clear
              </button>
            </div>
          </div>

          <div className="panel results-panel">
            <h2>Results</h2>
            <p className="panel-subtext">
              Uploaded file details and face-detection output
            </p>

            {results.length === 0 ? (
              <div className="empty-state">
                <p>No results yet.</p>
                <span>Upload an image to see stored path, face count, and coordinates.</span>
              </div>
            ) : (
              <div className="results-list">
                {results.map((result, index) => (
                  <article
                    key={`${result.filename}-${index}`}
                    className="result-card"
                  >
                    <div className="result-card-header">
                      <h3>{result.filename}</h3>
                      <span className="face-count">
                        Faces: {result.faces_detected ?? 0}
                      </span>
                    </div>

                    <div className="result-meta">
                      <p>
                        <strong>Local Path:</strong> {result.local_path}
                      </p>
                      <p>
                        <strong>Message:</strong> {result.message}
                      </p>
                    </div>

                    <div className="boxes-section">
                      <h4>Face Boxes</h4>
                      {result.face_boxes && result.face_boxes.length > 0 ? (
                        <ul className="box-list">
                          {result.face_boxes.map((box, i) => (
                            <li key={i} className="box-item">
                              <span>x: {box.x}</span>
                              <span>y: {box.y}</span>
                              <span>w: {box.width}</span>
                              <span>h: {box.height}</span>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="no-boxes">No faces detected.</p>
                      )}
                    </div>
                  </article>
                ))}
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}