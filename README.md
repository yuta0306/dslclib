# dslc6
対話システムライブコンペティションに使用できるPythonライブラリ

リファレンスは[https://yuta0306.github.io/dslclib/](https://yuta0306.github.io/dslclib/)にあります．

このライブラリに関する要望や質問は，yubo1336[at]lr.pi.titech.ac.jpまでお願いします．

## Changelog

### 2023/06/30

- `v0.1.2`をリリースしました．
- [https://yuta0306.github.io/dslclib/](https://yuta0306.github.io/dslclib/)にリファレンスを公開しました．
- `FaceRecognitinClient`→`FaceRecognitionClient`とタイポを修正しました．

### 2023/06/30

- `v0.1.3`をリリースしました．
- タイポを修正しました。

### 2023/07/06

- `v0.2.0`をリリースしました。
- EmotionType.fearをEmotionType.Fearに修正しました。
- FaceRecognitionServerの更新に伴い、face_recognition.pyにおけるモジュールをアップデートしました。
- OutputFor...とクライアントの出力をデータクラスで定義しました。
    - `OutputForFaceRecognition.emotion`と`OutputForFaceRecognition["emotion"]`の二つのアクセス方法を可能にしました。
- 型ヒントの一部をstrからLiteralに変更しました。

### 2023/09/28

- `v0.2.1`をリリースしました
- 稀に音声合成ができなくなるバグが発生したため，軽微な修正を加えました

### 2023/10/02

- `v0.3.0`をリリースしました
- 稀にキューがスタックして音声合成ができなくなるバグが発生したため，`Speech2TextClient`においてキューの監視を実装しました．以下が`Speech2TextClient.speech`メソッドにて追加された引数です．
    - `max_num_queue`: 最大キュー数．デフォルトは1
    - `wait_queue`: 送信コマンドが最大キュー数を超えた場合に，処理を待機するか，コマンドを破棄するか．デフォルトはFalse
- こまめにTTSコマンドを送信する場合は，`wait_queue=True`とすることで，全てのコマンドが実行されることが保証されます．
- 詳細の実装については公式リファレンスを参照してください．
- 問題が起きる場合は，Issueまたはプルリクエスト等を送ってください．
