import type { NextPage } from "next";
import { useCallback, useState } from "react";
import styles from "./create.module.css";
import Image from "next/image";
import NavBar from "@/components/NavBar";
import { redirect } from "next/navigation";
import Link from "next/link";
import { getAPIEndpoint } from ".";

const Create: NextPage = () => {
  const [file, setFile] = useState<any>();
  const [characters, setCharacters] = useState<string[]>();
  const [selectionScreen, setSelectionScreen] = useState<boolean>(false);

  const handleFileUpload = async (e: any) => {
    const file = e.target.files[0];
    setFile(file);
  };

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    // get the list of characters from the backend
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(`${getAPIEndpoint()}/api/characters`, {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    setCharacters(data.characters);
    setSelectionScreen(true);
  };

  return (
    <div className={styles.create}>
      <NavBar />
      <div className={styles.frameParent}>
        <div className={styles.createYourCosonaWrapper}>
          <b className={styles.createYourCosona}>Create Your Co:Sona</b>
        </div>
        <div className={styles.frameGroup}>
          {selectionScreen ? (
            <div>
              <div className={styles.selectTitle}>Select Characters!</div>
              <div className={styles.characterList}>
                {characters?.map((char, i) => {
                  return (
                    <Link key={char} href={`/Chat?character=${char}`} passHref>
                      <b className={`${styles.personas} justify-center`}>{char}</b>
                    </Link>
                  );
                })}
              </div>
            </div>
          ) : (
            <div>
              <div className={styles.characterimgWrapper}>
                <Image
                  className={styles.characterimgIcon1}
                  alt=""
                  src="user-alt.svg"
                  width={138}
                  height={138}
                />
              </div>
              <div className={styles.frameContainer}>
                <div className={styles.nameWrapper}>
                  <div className={styles.name}>File Upload</div>
                </div>
                <input
                  type="file"
                  onChange={handleFileUpload}
                  className={styles.uploadWrapper}></input>
                <div className="no-underline">
                  <form onSubmit={handleSubmit}>
                    <button className={styles.createYourCosonaContainer}>
                      <div className={styles.personas}>Create Your Co:Sona</div>
                    </button>
                  </form>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Create;
