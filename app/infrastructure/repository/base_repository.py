from firebase_admin import firestore

class BaseRepository:
    """
    모든 레포지토리의 기본 클래스.
    Firebase Firestore에 대한 기본 연결 및 공통 메소드를 제공합니다.
    """
    
    def __init__(self):
        """
        Firebase Firestore 클라이언트 초기화
        """
        self.db = firestore.client()
    
    def _convert_timestamp_to_iso(self, data):
        """
        Firestore Timestamp 객체를 ISO 형식 문자열로 변환합니다.
        
        Args:
            data: 변환할 데이터 (딕셔너리 또는 딕셔너리의 리스트)
            
        Returns:
            Timestamp가 ISO 문자열로 변환된 데이터
        """
        if isinstance(data, list):
            return [self._convert_timestamp_to_iso(item) for item in data]
        
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if hasattr(value, 'isoformat'):
                    result[key] = value.isoformat()
                elif isinstance(value, (dict, list)):
                    result[key] = self._convert_timestamp_to_iso(value)
                else:
                    result[key] = value
            return result
        
        return data
    
    def _get_server_timestamp(self):
        """
        Firestore 서버 타임스탬프를 반환합니다.
        
        Returns:
            Firestore 서버 타임스탬프
        """
        return firestore.SERVER_TIMESTAMP
    
    def _doc_to_dict(self, doc):
        """
        Firestore DocumentSnapshot을 딕셔너리로 변환하고 ID를 추가합니다.
        
        Args:
            doc: Firestore DocumentSnapshot 객체
            
        Returns:
            문서 ID와 데이터를 포함한 딕셔너리
        """
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return self._convert_timestamp_to_iso(data)
        return None
    
    def _docs_to_list(self, docs):
        """
        Firestore DocumentSnapshot 컬렉션을 딕셔너리 리스트로 변환합니다.
        
        Args:
            docs: Firestore DocumentSnapshot 객체의 컬렉션
            
        Returns:
            문서 데이터의 리스트
        """
        return [self._doc_to_dict(doc) for doc in docs] 