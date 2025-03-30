import React, { use } from "react";
import { Button, Table, Typography } from "antd";
import {
  UploadOutlined,
  FolderViewOutlined,
  DownloadOutlined,
  CloseOutlined,
} from "@ant-design/icons";
import "./userPage.css";
import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { v4 as uuidv4 } from "uuid";

interface Receipt {
  id: string;
  raw_text: string;
  store_name: string;
  time: string;
  date: string;
  image_url: string;
  user_uid: string;
  total_amount: number;
  store_address: string;
  processed_at: string;
  confidence_score: number;
}

const { Title } = Typography;

const handleViewReceipt = (imageUrl: string) => {
  console.log("Image URL: ", imageUrl);
  window.open(imageUrl, "_blank");
};

const columns = [
  {
    title: "Store Name",
    dataIndex: "storeName",
    key: "storeName",
  },
  {
    title: "Store Address",
    dataIndex: "storeAddress",
    key: "storeAddress",
  },
  {
    title: "Date",
    dataIndex: "date",
    key: "date",
    render: (text: string) => {
      const date = new Date(text);
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
      });
    },
  },
  {
    title: "Time",
    dataIndex: "time",
    key: "time",
  },
  {
    title: "Total Amount",
    dataIndex: "totalAmount",
    key: "totalAmount",
  },
  {
    title: "Processed Time",
    dataIndex: "processedTime",
    key: "processedTime",
    render: (text: string) => {
      const date = new Date(text);
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false,
      });
    },
  },
  {
    title: "View Receipt",
    dataIndex: "viewReceipt",
    key: "viewReceipt",
    render: (text: any, record: any) => (
      <FolderViewOutlined
        onClick={() => handleViewReceipt(record.imageUrl)}
        style={{ cursor: "pointer", fontSize: "25px", marginLeft: "25px" }}
      />
    ),
  },
];

const UserPage: React.FC = () => {
  const [user, setUser] = useState<any>(null);
  const navigate = useNavigate();
  const [receiptData, setReceiptData] = useState<any>([]);
  const [notifications, setNotifications] = useState<string[]>([]);

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    } else {
      navigate("/");
    }
  }, [navigate]);

  const fetchReceiptData = async (userUid: string): Promise<Receipt[]> => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/receipts/get-receipts-by-user/${userUid}`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch receipts");
      }

      const data = await response.json();

      return data;
    } catch (error) {
      console.error("Error fetching receipt data:", error);
      return [];
    }
  };

  const loadReceiptData = async () => {
    if (user) {
      const userUid = user.uid;
      const data = await fetchReceiptData(userUid);
      console.log("Fetched receipt data: ", data);

      const formattedData = data.map((receipt: Receipt) => ({
        key: receipt.id,
        storeName: receipt.store_name,
        storeAddress: receipt.store_address,
        date: receipt.date,
        time: receipt.time,
        totalAmount: receipt.total_amount,
        processedTime: receipt.processed_at,
        imageUrl: receipt.image_url,
      }));

      setReceiptData(formattedData);
    }
  };
  useEffect(() => {
    if (user) {
      loadReceiptData();
    }
  }, [user]);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    console.log("am intrat in handleFileUpload");
    if (file) {
      console.log("File selected: ", file);

      const userUid = user?.uid;
      console.log("User UID: ", userUid);

      if (!userUid) {
        console.error("User UID not found in local storage.");
        return;
      }

      // extrag extensia fisierului
      const fileExtension = file.name.split(".").pop();

      const newFileName = `receipt_${uuidv4()}.${fileExtension}`;

      // creez un obiect File cu numele nou
      const newFile = new File([file], newFileName, { type: file.type });

      // creez un formData pentru a trimite fisierul
      const formData = new FormData();
      formData.append("file", newFile);

      fetch(
        `http://localhost:8000/api/v1/bucket/upload_image/?folder=${userUid}`,
        {
          method: "POST",
          body: formData,
        }
      )
        .then((response) => {
          if (response.ok) {
            console.log("File uploaded successfully.");

            //actualizez lista de receipt-uri
          } else {
            console.error("Error uploading file.");
          }
        })
        .catch((error) => {
          console.error("Error: ", error);
        });
    } else {
      console.error("No file selected.");
    }
  };

  // receive notification when a new receipt is added

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8765");

    ws.onopen = () => {
      console.log("Connected to WebSocket server");
    };

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      const message = msg.message;
      //console.log("WebSocket message total:", msg);
      //console.log("WebSocket message received:", message);

      // Adaugă notificarea în listă
      const userUid = user?.uid;
      if (msg.user_uid === userUid) {
        setNotifications((prev) => [...prev, msg.message]);
        console.log("Notification received:", msg.message);

        if (message === "Receipt processed successfully") {
          loadReceiptData(); // Reîncarcă receipt-urile
        }
      } else {
        console.log("Not your receipt, not showing notification.");
        console.log("User UID: ", user?.uid);
        console.log("Message UID: ", msg.user_uid);
      }
    };

    ws.onclose = () => {
      console.log("WebSocket connection closed");
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    return () => {
      ws.close();
    };
  }, [user]);

  useEffect(() => {
    if (notifications.length > 0) {
      const timer = setTimeout(() => {
        setNotifications((prev) => prev.slice(1));
      }, 3000);

      return () => clearTimeout(timer);
    }
  }, [notifications]);

  const removeNotification = (index: any) => {
    setNotifications((prev) => prev.filter((_, i) => i !== index));
  };

  const handleDownloadExcel = async () => {
    if (!user?.uid) {
      console.error("UID-ul utilizatorului nu este disponibil.");
      return;
    }

    const response = await fetch(
      `http://localhost:8000/api/v1/stats/export-excel?uid=${user.uid}`
    );

    if (!response.ok) {
      console.error("Exportul a eșuat.");
      return;
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `raport_${user.uid}.xlsx`;
    link.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="user-page-container">
      <div>
        <Title level={2}>Welcome, {user?.displayName || "User"}!</Title>
      </div>
      <div>
        <Button
          className="upload-button"
          type="primary"
          icon={<UploadOutlined />}
          onClick={() => document.getElementById("file-upload")?.click()}
        >
          Upload Receipt
        </Button>

        <input
          id="file-upload"
          type="file"
          accept=".pdf,.png,.jpg,.jpeg"
          style={{ display: "none" }}
          onChange={handleFileUpload}
        />

        {/*Notificari*/}
        <div className="notifications-container">
          {notifications.map((notification, index) => (
            <div key={index} className="notification-popup">
              <span>{notification}</span>
              <CloseOutlined
                onClick={() => removeNotification(index)}
                style={{ cursor: "pointer", marginLeft: "10px" }}
              />
            </div>
          ))}
        </div>
      </div>
      <div>
        <Table
          columns={columns}
          dataSource={receiptData}
          className="user-table"
          rowKey="id"
          pagination={{ pageSize: 6 }}
        />
      </div>
      <div style={{ marginTop: "20px" }}>
        <Button
          className="download-button"
          type="primary"
          icon={<DownloadOutlined />}
          onClick={handleDownloadExcel}
        >
          Download Info
        </Button>
      </div>
    </div>
  );
};

export default UserPage;
