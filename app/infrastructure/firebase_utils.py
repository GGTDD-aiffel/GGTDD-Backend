from datetime import datetime

def convert_firebase_timestamp(firebase_datetime):
    if firebase_datetime is None:
        return None
    
    # firebase_datetime이 이미 datetime 객체인지 확인
    if isinstance(firebase_datetime, datetime):
        return firebase_datetime
    
    # DatetimeWithNanoseconds 변환
    return datetime(
        year=firebase_datetime.year,
        month=firebase_datetime.month,
        day=firebase_datetime.day,
        hour=firebase_datetime.hour,
        minute=firebase_datetime.minute,
        second=firebase_datetime.second,
        microsecond=firebase_datetime.microsecond
    )

def convert_firebase_MBTI(mbti_str):
    """
    MBTI 문자열(예: 'INTP')을 전체 용어 리스트로 변환합니다.
    예: 'INTP' -> ['Introverted', 'Intuitive', 'Thinking', 'Perceiving']
    
    Args:
        mbti_str: MBTI 유형을 나타내는 문자열
        
    Returns:
        문자열 리스트: 각 MBTI 차원의 전체 용어
    """
    if not mbti_str or not isinstance(mbti_str, str):
        return []
    
    # 입력 문자열 표준화
    mbti = mbti_str.upper().strip()
    
    # 유효성 검사
    if len(mbti) != 4:
        return []
    
    # MBTI 변환 매핑
    dimension_1 = {'E': 'Extraverted', 'I': 'Introverted'}
    dimension_2 = {'S': 'Sensing', 'N': 'Intuitive'}
    dimension_3 = {'T': 'Thinking', 'F': 'Feeling'}
    dimension_4 = {'J': 'Judging', 'P': 'Perceiving'}
    
    dimensions = [dimension_1, dimension_2, dimension_3, dimension_4]
    result = []
    
    # 각 차원 변환
    for i, char in enumerate(mbti):
        if i < len(dimensions) and char in dimensions[i]:
            result.append(dimensions[i][char])
        else:
            # 유효하지 않은 문자 발견
            return []
    
    return result