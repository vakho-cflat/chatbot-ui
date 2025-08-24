import { checkApiKey, getServerProfile } from "@/lib/server/server-chat-helpers"
import { ChatSettings } from "@/types"
import { GoogleGenerativeAI } from "@google/generative-ai"

export const runtime = "edge"

export async function POST(request: Request) {
  const json = await request.json()
  const { chatSettings, messages } = json as {
    chatSettings: ChatSettings
    messages: any[]
  }

  try {
    const profile = await getServerProfile()
    checkApiKey(profile.google_gemini_api_key, "Google")

    const genAI = new GoogleGenerativeAI(profile.google_gemini_api_key || "")
    const googleModel = genAI.getGenerativeModel({ model: chatSettings.model })

    const lastMessage = messages.pop()
    const userPrompt = lastMessage.parts[0].text

    // 🔍 Vector search (your local FastAPI server)
    const context = await fetch("http://localhost:5000/vector-search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: userPrompt })
    }).then(res => res.json())
    console.log("🔍 Vector matches received:", context.matches.map((m: any) => m.category))



    const contextText = context.matches.map(
      (m: any, i: number) => `${i + 1}. ${m.category}\nJSON:\n${JSON.stringify(m.full_json, null, 2)}`
    ).join("\n\n")
    
    const fullPrompt = `
    შემდეგი JSON მონაცემები დაკავშირებულია მომხმარებლის კითხვასთან. გამოიყენე ისინი სწორად:
    
    ${contextText}
    
    მომხმარებლის შეკითხვა: ${userPrompt}
    `.trim()

    const chat = googleModel.startChat({
      history: messages,
      generationConfig: {
        temperature: chatSettings.temperature
      }
    })

    const response = await chat.sendMessageStream([{ text: fullPrompt }])

    const encoder = new TextEncoder()
    const readableStream = new ReadableStream({
      async start(controller) {
        for await (const chunk of response.stream) {
          controller.enqueue(encoder.encode(chunk.text()))
        }
        controller.close()
      }
    })

    return new Response(readableStream, {
      headers: { "Content-Type": "text/plain" }
    })

  } catch (error: any) {
    let errorMessage = error.message || "An unexpected error occurred"
    const errorCode = error.status || 500

    if (errorMessage.toLowerCase().includes("api key not found")) {
      errorMessage =
        "Google Gemini API Key not found. Please set it in your profile settings."
    } else if (errorMessage.toLowerCase().includes("api key not valid")) {
      errorMessage =
        "Google Gemini API Key is incorrect. Please fix it in your profile settings."
    }

    return new Response(JSON.stringify({ message: errorMessage }), {
      status: errorCode
    })
  }
}


//import { checkApiKey, getServerProfile } from "@/lib/server/server-chat-helpers"
//import { ChatSettings } from "@/types"
//import { GoogleGenerativeAI } from "@google/generative-ai"
//
//export const runtime = "edge"
//
//export async function POST(request: Request) {
//  const json = await request.json()
//  const { chatSettings, messages } = json as {
//    chatSettings: ChatSettings
//    messages: any[]
//  }
//
//  try {
//    const profile = await getServerProfile()
//
//    checkApiKey(profile.google_gemini_api_key, "Google")
//
//    const genAI = new GoogleGenerativeAI(profile.google_gemini_api_key || "")
//    const googleModel = genAI.getGenerativeModel({ model: chatSettings.model })
//
//    const lastMessage = messages.pop()
//
//    const chat = googleModel.startChat({
//      history: messages,
//      generationConfig: {
//        temperature: chatSettings.temperature
//      }
//    })
//
//    const response = await chat.sendMessageStream(lastMessage.parts)
//
//    const encoder = new TextEncoder()
//    const readableStream = new ReadableStream({
//      async start(controller) {
//        for await (const chunk of response.stream) {
//          const chunkText = chunk.text()
//          controller.enqueue(encoder.encode(chunkText))
//        }
//        controller.close()
//      }
//    })
//
//    return new Response(readableStream, {
//      headers: { "Content-Type": "text/plain" }
//    })
//
//  } catch (error: any) {
//    let errorMessage = error.message || "An unexpected error occurred"
//    const errorCode = error.status || 500
//
//    if (errorMessage.toLowerCase().includes("api key not found")) {
//      errorMessage =
//        "Google Gemini API Key not found. Please set it in your profile settings."
//    } else if (errorMessage.toLowerCase().includes("api key not valid")) {
//      errorMessage =
//        "Google Gemini API Key is incorrect. Please fix it in your profile settings."
//    }
//
//    return new Response(JSON.stringify({ message: errorMessage }), {
//      status: errorCode
//    })
//  }
//}
