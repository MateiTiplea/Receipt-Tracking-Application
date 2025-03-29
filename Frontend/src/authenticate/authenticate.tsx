import { GoogleAuthProvider, signInWithPopup, User } from "firebase/auth";
import { auth } from "../firebase/firebaseConfig";
import { Button, Card, Typography } from "antd";
import { GoogleOutlined } from "@ant-design/icons";
import "./authenticate.css";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Authenticate() {
  const [user, setUser] = useState<null | User>(null);
  const navigate = useNavigate();

  const handleGoogle = async () => {
    try {
      const provider = new GoogleAuthProvider();
      const userCredential = await signInWithPopup(auth, provider);
      const user = userCredential.user;

      setUser(user);
      localStorage.setItem("user", JSON.stringify(user));
      console.log("User Info: ", user);

      // creez folderul utilizatorului in bucket
      const user_folder = user.uid;
      const response = await fetch(
        `http://localhost:8000/api/v1/bucket/create_folder_with_name/?folder_name=${user_folder}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (response.ok) {
        console.log("Folder created successfully in bucket.");
      } else {
        const errorData = await response.json();
        console.error("Error creating folder: ", errorData);
      }

      navigate("/user");
    } catch (error) {
      console.error("Error signing in: ", error);
    }
  };

  return (
    <div className="auth-container">
      <Card className="auth-card">
        <Typography.Title level={2}>Sign In</Typography.Title>
        <Button
          type="primary"
          icon={<GoogleOutlined />}
          onClick={handleGoogle}
          className="auth-button"
        >
          Sign in with Google
        </Button>
      </Card>
    </div>
  );
}
