import { IsString, IsOptional, IsArray } from 'class-validator';

export class ChatRequestDto {
  @IsString()
  message: string;

  @IsOptional()
  @IsArray()
  conversation_history?: { role: string; content: string }[];
}
