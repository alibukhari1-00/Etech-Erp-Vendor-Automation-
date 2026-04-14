import { Injectable, ServiceUnavailableException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { Response } from 'express';
import { UserEntity } from '../../database/entities/user.entity';
import { ChatRequestDto } from './ai-chat.dto';

const GREETINGS = new Set(['hi', 'hello', 'salam', 'hey', 'a o a', 'assalam o alaikum', 'good morning', 'good evening']);

@Injectable()
export class AiChatService {
  private agentsCache = new Map<string, any>();

  constructor(private readonly config: ConfigService) {}

  private getAgent(role: string, userName: string) {
    const key = `${role}_${userName}`;
    if (this.agentsCache.has(key)) return this.agentsCache.get(key);

    const apiKey = this.config.get<string>('app.openaiApiKey');
    if (!apiKey || apiKey === 'your-openai-api-key-here') {
      throw new ServiceUnavailableException('OpenAI API key is not configured. Add OPENAI_API_KEY to your .env file.');
    }

    const { ChatOpenAI } = require('langchain/chat_models/openai');
    const { SQLDatabase } = require('langchain/sql_db');
    const { createSqlAgent, SqlToolkit } = require('langchain/agents/toolkits/sql');
    const { MessagesPlaceholder } = require('langchain/prompts');

    const roleNote = role === 'purchaser'
      ? 'You are helping a Purchaser. Access to system user accounts is restricted. Focus on Vendors and Procurement.'
      : 'You are helping an Admin. You have full access to all business records, including system accounts.';

    const prefix = `You are the warm and professional "ETSolar ERP Assistant". You help ${userName} manage the business smoothly.\n\nOPERATING RULES:\n1. ERP Only: You only answer questions about ETSolar business data.\n2. NEVER output SQL queries or database internals.\n3. Security: ${roleNote}`;

    const dbUrl = this.config.get<string>('app.databaseUrl');
    const db = SQLDatabase.fromUri(dbUrl, { sampleRowsInTableInfo: 0 });
    const llm = new ChatOpenAI({ modelName: 'gpt-4o-mini', temperature: 0.2, openAIApiKey: apiKey });
    const toolkit = new SqlToolkit(db, llm);
    const agent = createSqlAgent(llm, toolkit, {
      prefix,
      extraPromptMessages: [new MessagesPlaceholder('chat_history')],
    });

    this.agentsCache.set(key, agent);
    return agent;
  }

  async streamAsk(dto: ChatRequestDto, user: UserEntity, res: Response) {
    const userName = user.full_name?.split(' ')[0] ?? 'there';
    const msgLower = dto.message.toLowerCase().trim().replace(/[?!.]+$/, '');

    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    if (GREETINGS.has(msgLower)) {
      const reply = `Hi ${userName}! 👋 I'm your ETSolar Assistant. I can help you find vendor details, check item stock, or track purchase demands. What would you like to check today? ☀️`;
      res.write(`data: ${JSON.stringify({ reply })}\n\n`);
      res.write('data: [DONE]\n\n');
      res.end();
      return;
    }

    try {
      const { HumanMessage, AIMessage } = require('langchain/schema');
      const history = (dto.conversation_history ?? []).map((m) =>
        m.role === 'user' ? new HumanMessage(m.content) : new AIMessage(m.content),
      );

      const agent = this.getAgent(user.role, userName);
      let inCodeBlock = false;

      const stream = await agent.streamEvents(
        { input: dto.message, chat_history: history },
        { version: 'v1' },
      );

      for await (const event of stream) {
        if (event.event === 'on_chat_model_stream') {
          const content = event.data?.chunk?.content;
          if (!content) continue;
          if (content.includes('```')) { inCodeBlock = !inCodeBlock; continue; }
          if (!inCodeBlock) res.write(`data: ${JSON.stringify({ reply: content })}\n\n`);
        }
      }
      res.write('data: [DONE]\n\n');
    } catch (e: any) {
      res.write(`data: ${JSON.stringify({ error: e.message ?? 'An error occurred' })}\n\n`);
    } finally {
      res.end();
    }
  }
}
