import { useEffect, useMemo, useState } from "react";
import type { ChangeEvent } from "react";
import "./App.css";

type FaceBox = {
  x: number;
  y: number;
  width: number;
  height: number;
};

type RecognizedFace = {
  name: string;
  distance?: number | null;
};

type SelectedImage = {
  file: File;
  previewUrl: string;
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
  recognized_faces?: RecognizedFace[];
};

type DisplayResult = UploadResponse & {
  previewUrl: string;
  imageWidth: number;
  imageHeight: number;
};

const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"];

function formatName(name: string | undefined) {
  if (!name || name === "unknown") return "Unknown";
  return name
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function loadImageMetadata(file: File): Promise<SelectedImage> {
  const previewUrl = URL.createObjectURL(file);

  return new Promise((resolve, reject) => {
    const image = new Image();

    image.onload = () => {
      resolve({
        file,
        previewUrl,
        width: image.naturalWidth,
        height: image.naturalHeight,
      });
    };

    image.onerror = () => {
      URL.revokeObjectURL(previewUrl);
      reject(new Error(`Could not load preview for ${file.name}`));
    };

    image.src = previewUrl;
  });
}

function loadPreviewImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();

    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error("Could not load image for download."));

    image.src = src;
  });
}

export default function App() {
  const [selectedFiles, setSelectedFiles] = useState<SelectedImage[]>([]);
  const [status, setStatus] = useState("Idle");
  const [results, setResults] = useState<DisplayResult[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const totalFilesLabel = useMemo(() => {
    if (selectedFiles.length === 0) return "No files selected";
    if (selectedFiles.length === 1) return "1 file selected";
    return `${selectedFiles.length} files selected`;
  }, [selectedFiles]);

  useEffect(() => {
    return () => {
      selectedFiles.forEach((selectedFile) => {
        URL.revokeObjectURL(selectedFile.previewUrl);
      });
    };
  }, [selectedFiles]);

  async function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files || []);
    const validFiles = files.filter((file) => ALLOWED_TYPES.includes(file.type));

    if (files.length === 0) {
      setSelectedFiles([]);
      setResults([]);
      setStatus("Idle");
      return;
    }

    if (validFiles.length !== files.length) {
      setStatus("Some files were skipped. Only JPG, PNG, and WEBP are allowed.");
    } else {
      setStatus("Files ready to upload.");
    }

    setResults([]);

    const nextSelectedFiles = await Promise.all(validFiles.map(loadImageMetadata));

    setSelectedFiles((currentFiles) => {
      currentFiles.forEach((selectedFile) => {
        URL.revokeObjectURL(selectedFile.previewUrl);
      });
      return nextSelectedFiles;
    });
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
      const uploadResults: DisplayResult[] = [];

      for (const selectedFile of selectedFiles) {
        const formData = new FormData();
        formData.append("file", selectedFile.file);

        const response = await fetch("http://127.0.0.1:8000/upload", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Upload failed for ${selectedFile.file.name}: ${errorText}`);
        }

        const data: UploadResponse = await response.json();
        uploadResults.push({
          ...data,
          previewUrl: selectedFile.previewUrl,
          imageWidth: selectedFile.width,
          imageHeight: selectedFile.height,
        });
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
    selectedFiles.forEach((selectedFile) => {
      URL.revokeObjectURL(selectedFile.previewUrl);
    });
    setSelectedFiles([]);
    setResults([]);
    setStatus("Idle");
  }

  async function handleDownloadResult(result: DisplayResult) {
    try {
      const image = await loadPreviewImage(result.previewUrl);
      const canvas = document.createElement("canvas");
      canvas.width = result.imageWidth;
      canvas.height = result.imageHeight;

      const context = canvas.getContext("2d");
      if (!context) {
        throw new Error("Canvas is not available in this browser.");
      }

      context.drawImage(image, 0, 0, result.imageWidth, result.imageHeight);

      const lineWidth = Math.max(3, Math.round(Math.min(result.imageWidth, result.imageHeight) * 0.006));
      const fontSize = Math.max(18, Math.round(Math.min(result.imageWidth, result.imageHeight) * 0.032));
      const labelPaddingX = Math.max(10, Math.round(fontSize * 0.55));
      const labelPaddingY = Math.max(6, Math.round(fontSize * 0.4));

      context.lineWidth = lineWidth;
      context.font = `700 ${fontSize}px Inter, Arial, sans-serif`;
      context.textBaseline = "top";

      result.face_boxes?.forEach((box, index) => {
        const recognizedFace = result.recognized_faces?.[index];
        const label = formatName(recognizedFace?.name);
        const isUnknown = recognizedFace?.name === "unknown" || !recognizedFace?.name;
        const strokeColor = isUnknown ? "#ff9f5a" : "#40e39b";

        context.strokeStyle = strokeColor;
        context.strokeRect(box.x, box.y, box.width, box.height);

        const textWidth = context.measureText(label).width;
        const labelWidth = textWidth + labelPaddingX * 2;
        const labelHeight = fontSize + labelPaddingY * 2;
        const labelX = Math.max(0, Math.min(box.x, result.imageWidth - labelWidth));
        const preferredLabelY = box.y - labelHeight;
        const labelY = preferredLabelY >= 0 ? preferredLabelY : Math.min(result.imageHeight - labelHeight, box.y);

        context.fillStyle = "rgba(8, 13, 24, 0.92)";
        context.fillRect(labelX, labelY, labelWidth, labelHeight);

        context.fillStyle = "#f7fbff";
        context.fillText(label, labelX + labelPaddingX, labelY + labelPaddingY);
      });

      const downloadUrl = canvas.toDataURL("image/png");
      const link = document.createElement("a");
      const baseFilename = result.filename.replace(/\.[^.]+$/, "");

      link.href = downloadUrl;
      link.download = `${baseFilename}-annotated.png`;
      link.click();
    } catch (error) {
      console.error(error);
      setStatus(
        error instanceof Error
          ? error.message
          : "Could not download the processed image."
      );
    }
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
                {selectedFiles.map((selectedFile) => (
                  <li
                    key={`${selectedFile.file.name}-${selectedFile.file.size}`}
                    className="file-item"
                  >
                    <span className="file-name">{selectedFile.file.name}</span>
                    <span className="file-size">
                      {(selectedFile.file.size / 1024).toFixed(1)} KB
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
                      <div className="result-card-actions">
                        <span className="face-count">
                          Faces: {result.faces_detected ?? 0}
                        </span>
                        <button
                          type="button"
                          className="download-button"
                          onClick={() => void handleDownloadResult(result)}
                        >
                          Download Result
                        </button>
                      </div>
                    </div>

                    <div className="result-meta">
                      <p>
                        <strong>Local Path:</strong> {result.local_path}
                      </p>
                      <p>
                        <strong>Message:</strong> {result.message}
                      </p>
                    </div>

                    <div className="preview-section">
                      <h4>Processed Image</h4>
                      <div className="image-preview-frame">
                        <div className="image-preview-stage">
                          <img
                            src={result.previewUrl}
                            alt={`Processed result for ${result.filename}`}
                            className="result-image"
                          />
                          {result.face_boxes?.map((box, i) => {
                            const recognizedFace = result.recognized_faces?.[i];
                            const label = formatName(recognizedFace?.name);
                            const isUnknown = recognizedFace?.name === "unknown" || !recognizedFace?.name;

                            return (
                              <div
                                key={`${result.filename}-face-${i}`}
                                className={`face-overlay ${isUnknown ? "unknown" : "matched"}`}
                                style={{
                                  left: `${(box.x / result.imageWidth) * 100}%`,
                                  top: `${(box.y / result.imageHeight) * 100}%`,
                                  width: `${(box.width / result.imageWidth) * 100}%`,
                                  height: `${(box.height / result.imageHeight) * 100}%`,
                                }}
                              >
                                <span className="face-label">{label}</span>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    </div>

                    <div className="boxes-section">
                      <h4>Detections</h4>
                      {result.face_boxes && result.face_boxes.length > 0 ? (
                        <ul className="box-list">
                          {result.face_boxes.map((box, i) => (
                            <li key={i} className="box-item">
                              <span>{formatName(result.recognized_faces?.[i]?.name)}</span>
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
