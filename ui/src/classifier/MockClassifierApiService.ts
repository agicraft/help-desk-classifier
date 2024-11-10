import { injectable, inject } from 'inversify';
import { ApiService } from '@/core/ApiService';
import type {
  ClassificationSchemaDto,
  ClassifiedMessageDto,
  ClassifyingMessageDto,
} from './classifier-dto';
import { ClassifierApiService } from './ClassifierApiService';

@injectable()
export class MockClassifierApiService extends ClassifierApiService {
  public async classify(data: ClassifyingMessageDto): Promise<ClassifiedMessageDto> {
    return {
      valid: false,
      attributes: [
        // { name: 'application_type', value: 'Ремонт' },
        // { name: 'device_type', value: 'Ноутбук' },
        // { name: 'model', value: 'X1704ZA-AU342' },
      ],
      // missingAttributes: ['vendor', 'serial_number'],
      missingAttributes: [],
      keywords: ['Ремонт', 'Apple, Asus', 'Ноутбук', 'X1704ZA-AU342', '12345, 12345-345-234'],
    };
  }
}
