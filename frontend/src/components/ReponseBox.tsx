// ResponseBox.js
import React from "react";
import styles from "./responseBox.module.css";
import Image from "next/image";

interface ResponseBoxProps {
  response: string;
  name: string;
  pictureSrc?: string; // Make pictureSrc optional
  loading?: boolean;
}

const ResponseBox: React.FC<ResponseBoxProps> = ({ response, name, loading, pictureSrc }) => {
  const isUser = name.trim() === "You";
  const defaultPicture = "user-alt.svg";

  return (
    <div className={`${styles.responseBox} ${isUser ? styles.userBackground : ""}`}>
      <Image
        src={pictureSrc || defaultPicture}
        alt=""
        className={styles.picture}
        width="42"
        height="42"
      />
      {loading ? (
        <div>Loading...</div>
      ) : (
      <div className={styles.content}>
        {isUser ? (
          <>
            <span className={styles.name}>You:</span>
            <span className={styles.response}>{response}</span>
          </>
        ) : (
          <>
            <span className={styles.name}>{name}:</span>
            <span className={styles.response}>{response}</span>
          </>
        )}        
      </div>
      )}
    </div>
  );
};

export default ResponseBox;
