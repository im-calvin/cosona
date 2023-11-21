import type { NextPage } from "next";
import Link from "next/link";
import { useEffect, useState, useRef } from "react";
import styles from "./chat.module.css";
import Image from "next/image";
import { MdOutlineSend } from "react-icons/md";
import CosanaBtn from "@/components/CosanaBtn";
import MenuBtn from "@/components/MenuBtn";
import { getAPIEndpoint } from "./index";
import ResponseBox from "@/components/ReponseBox";

type TChat = {
  message: string;
  loading: boolean;
};

const ChatDesignA: NextPage = () => {
  // odd is user input, even is chatbot output
  const [chat, setChat] = useState<TChat[]>([]);
  const [textareaInput, setTextareaInput] = useState<string>("");
  const [waitingForChat, setWaitingForChat] = useState<boolean>(false);
  const [character, setCharacter] = useState<string | null>("");

  // Event handler to update the state when the textarea value changes
  const handleTextareaChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (event.target.value === "\n") {
      return;
    }
    setTextareaInput(event.target.value);
  };

  // Event handler for the form submission
  const handleSubmit = async (
    event: React.FormEvent<HTMLFormElement> | React.KeyboardEvent<HTMLTextAreaElement>
  ) => {
    event.preventDefault();

    const currentInput = textareaInput.trim();

    // Determine if the submission is odd or even
    const isOddSubmission = chat.length % 2 !== 0;

    // Set loading state based on the submission type
    const newChatMessage = { message: currentInput, loading: isOddSubmission };

    const newChat = [...chat, newChatMessage, { message: "loading", loading: false }];
    setChat(newChat); // add loading message to chat
    setWaitingForChat(true);

    // parse json for display, and then set that to the chat state
    setTextareaInput("");

    // fetch response from bot
    // states are async
    fetchChat(newChat);
  };

  // newChat holds previous chats + current input
  // chat holds previous chats + current input + loading message
  const fetchChat = async (newChat: TChat[]) => {
    newChat.pop(); // remove the loading message
    const chatStr = newChat.map((message) => message.message);
    try {
      const response = await fetch(`${getAPIEndpoint()}/api/chat`, {
        method: "POST",
        body: JSON.stringify({
          text: chatStr, // Assuming you want to send all messages for context
          character: character,
        }),
        headers: {
          "Content-Type": "application/json",
        },
      });

      const json = await response.json();
      // copy the array, mutate the copy, then set the state
      const chatCopy = [...newChat];
      chatCopy[chatCopy.length - 1].loading = false; // un"loading" the loading message
      chatCopy[chatCopy.length - 1].message = json.message; // set the last message to the response
      console.log(chatCopy);
      setChat(chatCopy); // un"loading" the loading message
    } catch (error) {
      console.error("Error fetching chat:", error);
      // copy the array, mutate the copy, then set the state
      const chatCopy = [...chat];
      console.log(chat);
      chatCopy[chatCopy.length - 1].loading = false; // un"loading" the loading message
      chatCopy[chatCopy.length - 1].message = error as string; // set the last message to the response
      setChat(chatCopy); // un"loading" the loading message
    }
    setWaitingForChat(false);
  };

  // on page load, fetch the character we need to get from thee url
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const urlChar = urlParams.get("character");
    if (!urlChar) {
      setCharacter(null);
    }
    setCharacter(urlChar);
  }, []);

  // custom hook to check if component is mounted
  const useIsMount = () => {
    const isMountRef = useRef(true);
    useEffect(() => {
      isMountRef.current = false;
    }, []);
    return isMountRef.current;
  };

  return (
    <div className={styles.chatDesignA}>
      <div className={styles.mainFrame}>
        <div className={styles.colLeft}>
          <div className={styles.sideBar}>
            <Link href="/" className={styles.cosonaLogoParent}>
              <Image
                className={styles.cosonaLogoIcon}
                alt=""
                src="cosona-logo.svg"
                width={87}
                height={95}
              />
              <div className={styles.cosonasParent}>
                <b className={styles.cosonas}>Co:Sonas</b>
                <Image
                  className={styles.cohereLogoIcon}
                  alt=""
                  src="cohere-logo-white.svg"
                  width={218}
                  height={37}
                />
              </div>
            </Link>
            <div className={styles.frameParent}>
              <CosanaBtn text="Chats" href="" icon="chat" type="chatbtnsm" />
            </div>
            <div className={styles.frameGroup}>
              <CosanaBtn text="" href="/Create" icon="create" type="createbtnmd" />
              <CosanaBtn text="" href="/Personas" icon="persona" type="personasbtnmd" />
            </div>
            <MenuBtn name="Character 1" selected={true} />
            <MenuBtn name="Character 2" href="/Chat?character=tonystark" selected={false} />
            <MenuBtn name="Character 3" selected={false} />
            <MenuBtn name="Character 4" selected={false} />
            <MenuBtn name="Character 5" selected={false} />
          </div>
        </div>
        <div className={styles.colRight}>
          <div className={styles.responseContainer}>
            <div>
              {chat.map((message, index) => (
                <ResponseBox
                  key={index}
                  response={message.message}
                  name={index % 2 === 0 ? "You" : `${character}`}
                  pictureSrc={index % 2 === 0 ? "" : `${convertCharToImgSrc(character as string)}`}
                  loading={message.loading}
                />
              ))}
            </div>

            {/* if !character */}
            {!character && (
              <CosanaBtn text="Go to Personas" href="/Personas" icon="persona" type="personabtn" />
            )}
          </div>

          <div className={styles.chatContainer}>
            <form onSubmit={handleSubmit} className={styles.inputContainer}>
              <textarea
                className={styles.inputContainer}
                onChange={handleTextareaChange}
                value={textareaInput}
                placeholder={`Type a message to ${character}`}
                disabled={!character || waitingForChat}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey && textareaInput !== "") {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
              />
              <button
                style={{ alignSelf: "center", background: "none", border: "none" }}
                type="submit">
                <MdOutlineSend />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatDesignA;

function convertCharToImgSrc(character: string) {
  switch (character) {
    case "sasuke":
      return "sasuke.svg";
    case "tonystark":
      return "tony.svg";
    case "yoda":
      return "yoda.svg";
    case "harrypotter":
      return "harry.svg";
    case "ricksanchez":
      return "rick.svg";
    case "sherlock":
      return "sherlock.svg";
    default:
      return "user-alt.svg";
  }
}
