# reference/

캐릭터 외형의 기준이 되는 원본 이미지를 두는 곳이다.

- `kungkung_official_reference.png` — 사용자가 제공한 쿵쿵이 공식 레퍼런스
  (민트그린 피부 + 크림색 배, 복숭아색 뿔 3개, 열대 꽃무늬 아이보리 반다나,
  녹갈색 큰 눈). `prompts/characters.json`의 쿵쿵 묘사가 이 이미지에 맞춰져 있다.

이 이미지는 저장소에 함께 커밋되어 있다.

`Qwen-Image-Edit` 계열 Space로 레퍼런스 기반 각도 변형을 할 때 입력으로 쓴다
(해당 Space는 파일이 아니라 **base64 문자열**(`image_b64`)을 받는다 — README 참고).
