import { LLM } from "@/types"

const OPENAI_PLATFORM_LINK = "https://platform.openai.com/docs/overview"

// GPT-4o (Flagship, multimodal)
const GPT4o: LLM = {
  modelId: "gpt-4o",
  modelName: "GPT-4o",
  provider: "openai",
  hostedId: "gpt-4o",
  platformLink: OPENAI_PLATFORM_LINK,
  imageInput: true,
  pricing: {
    currency: "USD",
    unit: "1M tokens",
    inputCost: 5,
    outputCost: 15
  }
}

// GPT-4 (Standard)
const GPT4: LLM = {
  modelId: "gpt-4",
  modelName: "GPT-4",
  provider: "openai",
  hostedId: "gpt-4",
  platformLink: OPENAI_PLATFORM_LINK,
  imageInput: false,
  pricing: {
    currency: "USD",
    unit: "1M tokens",
    inputCost: 30,
    outputCost: 60
  }
}

// GPT-3.5 Turbo (Default fallback)
const GPT35Turbo: LLM = {
  modelId: "gpt-3.5-turbo",
  modelName: "GPT-3.5 Turbo",
  provider: "openai",
  hostedId: "gpt-3.5-turbo",
  platformLink: OPENAI_PLATFORM_LINK,
  imageInput: false,
  pricing: {
    currency: "USD",
    unit: "1M tokens",
    inputCost: 0.5,
    outputCost: 1.5
  }
}

// GPT-3.5 Turbo Instruct
const GPT35TurboInstruct: LLM = {
  modelId: "gpt-3.5-turbo-instruct",
  modelName: "GPT-3.5 Turbo Instruct",
  provider: "openai",
  hostedId: "gpt-3.5-turbo-instruct",
  platformLink: OPENAI_PLATFORM_LINK,
  imageInput: false,
  pricing: {
    currency: "USD",
    unit: "1M tokens",
    inputCost: 1.5,
    outputCost: 1.5
  }
}

// GPT-3.5 Turbo 16K
const GPT35Turbo16k: LLM = {
  modelId: "gpt-3.5-turbo-16k",
  modelName: "GPT-3.5 Turbo 16K",
  provider: "openai",
  hostedId: "gpt-3.5-turbo-16k",
  platformLink: OPENAI_PLATFORM_LINK,
  imageInput: false,
  pricing: {
    currency: "USD",
    unit: "1M tokens",
    inputCost: 0.5,
    outputCost: 1.5
  }
}

// GPT-4o Mini
const GPT4oMini: LLM = {
  modelId: "gpt-4o-mini",
  modelName: "GPT-4o Mini",
  provider: "openai",
  hostedId: "gpt-4o-mini",
  platformLink: OPENAI_PLATFORM_LINK,
  imageInput: true,
  pricing: {
    currency: "USD",
    unit: "1M tokens",
    inputCost: 2,
    outputCost: 6
  }
}

// GPT-4.5 Preview (if active)
const GPT45Preview: LLM = {
  modelId: "gpt-4.5-preview",
  modelName: "GPT-4.5 Preview",
  provider: "openai",
  hostedId: "gpt-4.5-preview",
  platformLink: OPENAI_PLATFORM_LINK,
  imageInput: false,
  pricing: {
    currency: "USD",
    unit: "1M tokens",
    inputCost: 15,
    outputCost: 45
  }
}

// Export all usable chat models
export const OPENAI_LLM_LIST: LLM[] = [
  GPT4o,
  GPT4oMini,
  GPT4,
  GPT45Preview,
  GPT35Turbo,
  GPT35Turbo16k,
  GPT35TurboInstruct
]

