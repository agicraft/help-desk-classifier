export interface ClassificationSchemaDto {
  attributeLabels: Record<string, string>;
}

export interface ClassifyingMessageDto {
  name?: string;
  topic?: string;
  text: string;
  generateAnswer: boolean;
}

export interface ClassifierAttributeDto {
  name: string;
  value: any;
}

export interface ClassifiedMessageDto {
  valid: boolean;
  attributes: ClassifierAttributeDto[];
  missingAttributes: string[];
  keywords: string[];
  answer?: string;
}
