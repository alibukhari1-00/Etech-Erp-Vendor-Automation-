import { IsBoolean } from 'class-validator';

export class PurchaserAccessUpdateDto {
  @IsBoolean()
  purchaser_access_enabled: boolean;
}
