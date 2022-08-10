Login is too hard to do.

目前是Fake login。

在檢測時，只有事先在generate_frames()中的name變數指定的學號，檢測資料才會更新到資料庫裡面。

目前預設指定給name的學號是108403000，如果在首頁輸入的學號不是此學號，那你檢測完後，檢測資料都會被存進user_id為108403000的欄位中，而不是你輸入的學號中，哈哈。
（但你輸入的學號還是會匯入資料庫，只是檢測資料值不管怎樣都會是０）

記得去http://dlib.net/files/ 下載shape_predictor_68_face_landmarks.dat.bz2 放到根目錄才能執行喔喔
