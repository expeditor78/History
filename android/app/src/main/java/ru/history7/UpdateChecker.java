package ru.history7;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageInfo;
import android.net.Uri;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.widget.Toast;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

/** Проверяет только публичный файл релиза; никаких ключей и разрешений на установку. */
final class UpdateChecker {
    private static final String MANIFEST =
            "https://github.com/expeditor78/History/releases/latest/download/update.json";
    private static final long DAY = 24L * 60 * 60 * 1000;
    private final Activity activity;
    private final SharedPreferences prefs;
    private final Handler main = new Handler(Looper.getMainLooper());
    private final ExecutorService worker = Executors.newSingleThreadExecutor();
    private final AtomicBoolean busy = new AtomicBoolean(false);
    private volatile boolean closed;
    private volatile HttpURLConnection connection;
    private AlertDialog dialog;

    UpdateChecker(Activity activity) {
        this.activity = activity;
        prefs = activity.getSharedPreferences("updates", Activity.MODE_PRIVATE);
    }

    void check(boolean manual) {
        if (closed) return;
        long elapsed = System.currentTimeMillis() - prefs.getLong("checkedAt", 0);
        if (!manual && elapsed >= 0 && elapsed < DAY) return;
        if (!busy.compareAndSet(false, true)) {
            if (manual) toast("Проверка уже идёт…");
            return;
        }
        if (manual) toast("Проверяем обновления…");
        worker.execute(() -> {
            try {
                JSONObject data = readManifest();
                long latestCode = data.getLong("versionCode");
                String latestName = data.getString("versionName");
                String apkUrl = data.getString("apkUrl");
                Uri apk = Uri.parse(apkUrl);
                // Ссылка должна вести только на APK нашего публичного репозитория.
                if (latestCode <= 0 || latestName.isEmpty() || latestName.length() > 64
                        || !"https".equals(apk.getScheme()) || !"github.com".equals(apk.getHost())
                        || apk.getPort() != -1 || apk.getUserInfo() != null
                        || apk.getQuery() != null || apk.getFragment() != null
                        || !apk.getPath().matches("/expeditor78/History/releases/download/apk-[0-9]+/History7\\.apk")) {
                    throw new IllegalArgumentException("Некорректный файл обновления");
                }
                PackageInfo installed = activity.getPackageManager()
                        .getPackageInfo(activity.getPackageName(), 0);
                long current = Build.VERSION.SDK_INT >= 28
                        ? installed.getLongVersionCode() : installed.versionCode;
                prefs.edit().putLong("checkedAt", System.currentTimeMillis()).apply();
                main.post(() -> {
                    if (!available()) return;
                    if (latestCode > current) {
                        if (!manual && prefs.getLong("offeredCode", 0) == latestCode) return;
                        if (dialog != null && dialog.isShowing()) return;
                        prefs.edit().putLong("offeredCode", latestCode).apply();
                        dialog = new AlertDialog.Builder(activity)
                                .setTitle("Есть обновление")
                                .setMessage("Доступна версия " + latestName + " (сборка " + latestCode
                                        + "). Сейчас установлена сборка " + current
                                        + ".\n\nСкачать APK? Он откроется в браузере. Установку нужно подтвердить самому; приложение не удаляй — так сохранится прогресс.")
                                .setPositiveButton("Скачать APK", (d, which) -> {
                                    try {
                                        activity.startActivity(new Intent(Intent.ACTION_VIEW, apk));
                                    } catch (Exception e) {
                                        toast("Не удалось открыть браузер для скачивания.");
                                    }
                                })
                                .setNegativeButton("Позже", null).create();
                        dialog.show();
                    } else if (manual) {
                        toast("У тебя последняя версия (сборка " + current + ").");
                    }
                });
            } catch (Exception e) {
                if (manual) main.post(() -> {
                    if (available()) toast("Не удалось проверить обновления. Проверь интернет и попробуй ещё раз.");
                });
            } finally {
                busy.set(false);
            }
        });
    }

    private JSONObject readManifest() throws Exception {
        URL url = new URL(MANIFEST);
        // GitHub перенаправляет запрос на хранилище артефактов; разрешаем лишь HTTPS.
        for (int redirects = 0; redirects <= 5; redirects++) {
            if (closed) throw new IllegalStateException("Закрыто");
            if (!"https".equals(url.getProtocol())) throw new IllegalArgumentException("HTTPS required");
            HttpURLConnection c = (HttpURLConnection) url.openConnection();
            connection = c;
            c.setConnectTimeout(8000);
            c.setReadTimeout(8000);
            c.setInstanceFollowRedirects(false);
            c.setUseCaches(false);
            c.setRequestProperty("User-Agent", "History7-Android");
            c.setRequestProperty("Accept", "application/json");
            try {
                int status = c.getResponseCode();
                if (status == 301 || status == 302 || status == 303 || status == 307 || status == 308) {
                    String location = c.getHeaderField("Location");
                    if (location == null) throw new IllegalStateException("Redirect without location");
                    url = new URL(url, location);
                    continue;
                }
                if (status != 200) throw new IllegalStateException("HTTP " + status);
                try (InputStream in = c.getInputStream(); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
                    byte[] buffer = new byte[2048];
                    int n;
                    while ((n = in.read(buffer)) != -1) {
                        if (closed || out.size() + n > 16384) throw new IllegalStateException("Ответ слишком большой");
                        out.write(buffer, 0, n);
                    }
                    return new JSONObject(new String(out.toByteArray(), StandardCharsets.UTF_8));
                }
            } finally {
                c.disconnect();
                connection = null;
            }
        }
        throw new IllegalStateException("Слишком много перенаправлений");
    }

    private boolean available() {
        return !closed && !activity.isFinishing() && !activity.isDestroyed();
    }

    private void toast(String text) {
        if (available()) Toast.makeText(activity, text, Toast.LENGTH_LONG).show();
    }

    void close() {
        closed = true;
        HttpURLConnection c = connection;
        if (c != null) c.disconnect();
        worker.shutdownNow();
        main.removeCallbacksAndMessages(null);
        if (dialog != null) dialog.dismiss();
    }
}
