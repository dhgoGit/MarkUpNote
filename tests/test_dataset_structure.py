import datasets

def main():
    # 데이터셋 로드
    dataset = datasets.load_dataset("corto-ai/handwritten-text", split="train[:1]")
    
    # 첫 번째 샘플 가져오기
    sample = dataset[0]
    
    # 데이터셋 구조 출력
    print("\n데이터셋 특성:")
    print(dataset.features)
    
    print("\n첫 번째 샘플 키:")
    print(sample.keys())
    
    print("\n이미지 데이터 타입:")
    print(type(sample['image']))
    
    if hasattr(sample['image'], 'shape'):
        print("\n이미지 shape:")
        print(sample['image'].shape)
    
    print("\n텍스트 데이터:")
    print(sample['text'])

if __name__ == '__main__':
    main() 