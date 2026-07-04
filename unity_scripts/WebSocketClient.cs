using System;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;

[Serializable]
public class ChatMessage
{
    public string text;
    public string personality;
}

[Serializable]
public class ServerResponse
{
    public string type;
    public string text;
    // public float[] visemes; 
    // public string audio_url;
}

public class WebSocketClient : MonoBehaviour
{
    public string serverUrl = "ws://localhost:8001/ws/chat";
    private ClientWebSocket ws;
    public LipSyncController lipSyncController; // Reference to LipSync controller

    async void Start()
    {
        ws = new ClientWebSocket();
        try
        {
            await ws.ConnectAsync(new Uri(serverUrl), CancellationToken.None);
            Debug.Log("Connected to Trinity AI Server");
            ReceiveMessages();
        }
        catch (Exception e)
        {
            Debug.LogError("Connection error: " + e.Message);
        }
    }

    public async void SendMessageToServer(string messageText, string personality)
    {
        if (ws.State == WebSocketState.Open)
        {
            ChatMessage msg = new ChatMessage { text = messageText, personality = personality };
            string json = JsonUtility.ToJson(msg);
            byte[] bytes = Encoding.UTF8.GetBytes(json);
            await ws.SendAsync(new ArraySegment<byte>(bytes), WebSocketMessageType.Text, true, CancellationToken.None);
        }
    }

    private async void ReceiveMessages()
    {
        byte[] buffer = new byte[1024 * 4];
        while (ws.State == WebSocketState.Open)
        {
            WebSocketReceiveResult result = await ws.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None);
            if (result.MessageType == WebSocketMessageType.Text)
            {
                string message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                ServerResponse response = JsonUtility.FromJson<ServerResponse>(message);
                
                Debug.Log("AI: " + response.text);
                
                // If using lip sync and TTS:
                // if (response.visemes != null && lipSyncController != null) {
                //     lipSyncController.PlayVisemes(response.visemes);
                // }
            }
        }
    }

    private async void OnDestroy()
    {
        if (ws != null && ws.State == WebSocketState.Open)
        {
            await ws.CloseAsync(WebSocketCloseStatus.NormalClosure, string.Empty, CancellationToken.None);
        }
    }
}
