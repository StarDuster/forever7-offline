package com.forever7.offline;

import android.app.Activity;
import android.content.*;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.widget.*;
import java.io.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;
import org.json.*;

/** Single installed application's first-use resource check and SAF importer. */
public class ResourceInitActivity extends Activity {
    private static final int PICK = 701;
    private final AtomicBoolean cancelled = new AtomicBoolean(false);
    private TextView status;
    private Button select, retry, cancel, sourceSettings;
    private boolean busy, dead;
    private boolean gameHandedOff;
    private long lastProgress;
    private String manifestId;
    private ResourceImporter importer;
    private JSONObject sourcePlan;
    private final List<ResourceImporter.Entry> resourceEntries = new ArrayList<ResourceImporter.Entry>();

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout column = new LinearLayout(this);
        column.setOrientation(LinearLayout.VERTICAL);
        int pad = (int)(24 * getResources().getDisplayMetrics().density);
        column.setPadding(pad, pad, pad, pad);
        TextView title = new TextView(this);
        title.setText("永远的七日之都 · 离线资源准备"); title.setTextSize(22);
        column.addView(title);
        status = new TextView(this); status.setTextSize(16); column.addView(status);
        select = new Button(this); select.setText("选择本地资源 ZIP"); column.addView(select);
        retry = new Button(this); retry.setText("重试下载 / 完整检查"); column.addView(retry);
        sourceSettings = new Button(this); sourceSettings.setText("备用素材源设置（可选）"); column.addView(sourceSettings);
        cancel = new Button(this); cancel.setText("取消准备"); column.addView(cancel);
        ScrollView scroll = new ScrollView(this); scroll.addView(column); setContentView(scroll);
        select.setOnClickListener(new View.OnClickListener() { public void onClick(View v) {
            Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
            intent.addCategory(Intent.CATEGORY_OPENABLE); intent.setType("application/zip");
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
            startActivityForResult(intent, PICK);
        }});
        retry.setOnClickListener(new View.OnClickListener() { public void onClick(View v) { run(null, true); }});
        sourceSettings.setOnClickListener(new View.OnClickListener() { public void onClick(View v) { showSourceSettings(); }});
        cancel.setOnClickListener(new View.OnClickListener() { public void onClick(View v) {
            if (busy) cancelled.set(true); else finish();
        }});
        run(null, false);
    }
    private void showSourceSettings() {
        if (busy) return;
        final android.content.SharedPreferences preferences = getSharedPreferences("offline_resource_sources", MODE_PRIVATE);
        LinearLayout content = new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        int padding = (int)(20 * getResources().getDisplayMetrics().density);
        content.setPadding(padding, padding, padding, padding);
        TextView explanation = new TextView(this);
        explanation.setText("始终优先官方固定版本；官方失败后才尝试备用源。所有素材仍按应用内固定清单校验。\n请输入包含 patch2.android.640/ 目录的 HTTPS 基础 URL；不会上传文件。留空或清除后只使用官方源。设置后点击“重试下载 / 完整检查”。");
        content.addView(explanation);
        final EditText address = new EditText(this);
        address.setSingleLine(true);
        address.setInputType(android.text.InputType.TYPE_CLASS_TEXT | android.text.InputType.TYPE_TEXT_VARIATION_URI);
        address.setHint("HTTPS 基础 URL（可选）");
        address.setText(preferences.getString("mirror_base_url", ""));
        content.addView(address);
        final android.app.AlertDialog dialog = new android.app.AlertDialog.Builder(this)
            .setTitle("备用素材源") .setView(content)
            .setPositiveButton("保存", null).setNeutralButton("清除", null)
            .setNegativeButton("取消", null).create();
        dialog.setOnShowListener(new DialogInterface.OnShowListener() { public void onShow(DialogInterface ignored) {
            dialog.getButton(android.app.AlertDialog.BUTTON_POSITIVE).setOnClickListener(new View.OnClickListener() { public void onClick(View v) {
                String value = address.getText().toString().trim();
                if (!value.isEmpty()) {
                    try {
                        java.net.URI parsed = new java.net.URI(value);
                        if (!"https".equals(parsed.getScheme()) || parsed.getHost() == null || parsed.getUserInfo() != null
                            || parsed.getRawQuery() != null || parsed.getRawFragment() != null)
                            throw new IllegalArgumentException();
                    } catch (Exception invalid) { address.setError("请输入有效 HTTPS 基础 URL，不含账号、查询参数或片段"); return; }
                }
                android.content.SharedPreferences.Editor editor = preferences.edit();
                if (value.isEmpty()) editor.remove("mirror_base_url"); else editor.putString("mirror_base_url", value);
                if (!editor.commit()) { address.setError("设置保存失败，请重试"); return; }
                dialog.dismiss();
                status.setText("素材源设置已保存。官方源始终优先；点击“重试下载 / 完整检查”继续，或选择本地资源 ZIP。");
            }});
            dialog.getButton(android.app.AlertDialog.BUTTON_NEUTRAL).setOnClickListener(new View.OnClickListener() { public void onClick(View v) {
                if (!preferences.edit().remove("mirror_base_url").commit()) { address.setError("设置清除失败，请重试"); return; }
                dialog.dismiss(); status.setText("已清除备用素材源。点击“重试下载 / 完整检查”使用官方源，或选择本地资源 ZIP。");
            }});
        }});
        dialog.show();
    }
    private ResourceImporter createImporter() throws Exception {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        try (InputStream input = getAssets().open("offline_resource_manifest.json")) {
            byte[] buffer = new byte[16384]; int n;
            while ((n = input.read(buffer)) != -1) bytes.write(buffer, 0, n);
        }
        JSONObject manifest = new JSONObject(new String(bytes.toByteArray(), "UTF-8"));
        manifestId = manifest.getString("id");
        sourcePlan = manifest.getJSONObject("official_source_plan");
        JSONArray rows = manifest.getJSONArray("entries");
        List<ResourceImporter.Entry> entries = new ArrayList<ResourceImporter.Entry>();
        for (int i = 0; i < rows.length(); i++) {
            JSONObject row = rows.getJSONObject(i);
            entries.add(new ResourceImporter.Entry(row.getString("name"), row.getLong("bytes"), row.getString("sha256")));
        }
        resourceEntries.clear(); resourceEntries.addAll(entries);
        final android.content.SharedPreferences cache = getSharedPreferences("offline_resource_verification", MODE_PRIVATE);
        File external = getExternalFilesDir(null);
        if (external == null) throw new IOException("应用资源目录不可用");
        return new ResourceImporter(new File(external, "netease/qrzd/Documents/res"), entries,
            new ResourceImporter.Cache() {
                private String fingerprint(ResourceImporter.Entry entry, File file) {
                    return manifestId + ":" + entry.sha256 + ":" + file.length() + ":" + file.lastModified();
                }
                public boolean verified(ResourceImporter.Entry entry, File file) {
                    return cache.getString(entry.name, "").equals(fingerprint(entry, file));
                }
                public void remember(ResourceImporter.Entry entry, File file) {
                    if (!cache.edit().putString(entry.name, fingerprint(entry, file)).commit())
                        throw new IllegalStateException("Resource verification cache write failed");
                }
                public void invalidate(ResourceImporter.Entry entry) {
                    if (!cache.edit().remove(entry.name).commit())
                        throw new IllegalStateException("Resource verification cache write failed");
                }
            }, cancelled, new ResourceImporter.Progress() {
                public void update(final String name, final long bytes, final long total) {
                    long now = android.os.SystemClock.uptimeMillis();
                    if (now - lastProgress < 200 && bytes != total) return;
                    lastProgress = now;
                    runOnUiThread(new Runnable() { public void run() {
                        if (!dead) status.setText("正在检查 / 导入 " + name + "\n" + bytes / 1048576 + " / " + total / 1048576 + " MiB");
                    }});
                }
            });
    }
    private void run(final Uri uri, final boolean force) {
        if (busy) return;
        busy = true; cancelled.set(false); select.setEnabled(false); retry.setEnabled(false); sourceSettings.setEnabled(false);
        status.setText("素材约 7.5 GiB；首次下载加缓存峰值约 15 GiB，并需额外系统余量。缺失资源将自动从官方固定版本下载。已验证文件会保留，离线存档不会改动。");
        new Thread(new Runnable() { public void run() {
            try {
                final List<String> missing;
                final boolean reuse = reusePreparedGame(cancelled);
                if (cancelled.get()) throw new ResourceImporter.Cancelled();
                if (reuse) {
                    missing = Collections.emptyList();
                } else {
                try (ResourceImporter session = createImporter()) {
                importer = session;
                importer.removeInterruptedTemporaryFiles();
                if (uri != null) {
                    InputStream input = getContentResolver().openInputStream(uri);
                    if (input == null) throw new IOException("无法打开所选资源");
                    try (InputStream source = input) { importer.importZip(source, force); }
                }
                List<String> initialMissing = importer.missing(force);
                if (!initialMissing.isEmpty() && uri == null) downloadOfficial(session);
                missing = importer.missing(false);
                }
                }
                // A backend hook may need a fresh exclusive importer session. Close
                // the download/import session before calling it or posting launch.
                if (cancelled.get()) throw new ResourceImporter.Cancelled();
                if (missing.isEmpty() && !reuse) {
                    File external = getExternalFilesDir(null);
                    if (external == null) throw new IOException("应用资源目录不可用");
                    prepareGame(new File(external, "netease/qrzd/Documents"),
                        Collections.unmodifiableList(new ArrayList<ResourceImporter.Entry>(resourceEntries)), cancelled);
                }
                if (cancelled.get()) throw new ResourceImporter.Cancelled();
                runOnUiThread(new Runnable() { public void run() {
                    if (dead) return;
                    idle();
                    if (cancelled.get()) {
                        preparationAbandoned();
                        status.setText("已取消。已验证文件与存档仍保留。");
                    }
                    else if (missing.isEmpty()) launchGame();
                    else status.setText("还缺少或损坏 " + missing.size() + " 个资源文件。\n请选择完整本地资源 ZIP；导入可中断后重试。\n" + missing.get(0));
                }});
            } catch (final Exception error) {
                try { preparationAbandoned(); }
                catch (RuntimeException cleanup) { error.addSuppressed(cleanup); }
                runOnUiThread(new Runnable() { public void run() {
                    if (dead) return;
                    idle(); status.setText(error instanceof ResourceImporter.Cancelled ? "已取消。已验证文件与存档仍保留。" : "资源准备未完成：\n" + error.getMessage() + "\n可设置备用素材源后重试下载，或选择本地资源 ZIP。");
                }});
            } finally {
                preparationWorkerFinished();
            }
        }}, "offline-resource-init").start();
    }
    private OfficialResources.Payload payload(JSONObject row, String sha) throws JSONException {
        return new OfficialResources.Payload(row.getString("path"), row.getLong("size"), row.getString("md5"), sha);
    }
    private void downloadOfficial(ResourceImporter session) throws Exception {
        List<OfficialResources.Part> parts = new ArrayList<OfficialResources.Part>();
        JSONArray sourceParts = sourcePlan.getJSONArray("parts");
        for (int i=0; i<sourceParts.length(); i++) {
            JSONObject row=sourceParts.getJSONObject(i); OfficialResources.Part part=new OfficialResources.Part();
            part.name=row.getString("part"); if(part.name.equals("script"))throw new IOException("Script source forbidden");
            part.check=payload(row.getJSONObject("check"),row.getString("check_sha256"));
            JSONArray data=row.getJSONArray("payloads"); for(int j=0;j<data.length();j++)part.payloads.add(payload(data.getJSONObject(j),null));
            parts.add(part);
        }
        Map<String,ResourceImporter.Entry> entries=new HashMap<String,ResourceImporter.Entry>();
        for(ResourceImporter.Entry entry:resourceEntries)entries.put(entry.name,entry);
        List<OfficialResources.Raw> raws=new ArrayList<OfficialResources.Raw>();JSONArray raw=sourcePlan.getJSONArray("raw_files");
        for(int i=0;i<raw.length();i++){JSONObject row=raw.getJSONObject(i);OfficialResources.Raw value=new OfficialResources.Raw();String rawPath=row.getString("path");if(!rawPath.startsWith("res/"))throw new IOException("Invalid pinned raw path");value.entry=entries.get(rawPath.substring(4));if(value.entry==null)throw new IOException("Missing pinned raw output");value.offset=row.getLong("offset");value.version=row.getInt("version");raws.add(value);}
        String mirror=getSharedPreferences("offline_resource_sources",MODE_PRIVATE).getString("mirror_base_url",null);
        new OfficialResources(session,new File(getExternalFilesDir(null),"offline-source-cache"),mirror).prepare(parts,entries,raws);
    }
    private void idle() { busy = false; select.setEnabled(true); retry.setEnabled(true); sourceSettings.setEnabled(true); }
    /** Worker-only extension point, after closing the download/import session.
     * Throw on incomplete backend preparation. Legacy builds need no backend here.
     */
    protected void prepareGame(File documents, List<ResourceImporter.Entry> entries,
                               AtomicBoolean cancellation) throws Exception { }
    /** Worker-only, BEFORE opening or mutating any resource session. A backend
     * may atomically lease its current ready game or reserve this preparation.
     * true skips import/download and reuses that live generation's evidence.
     */
    protected boolean reusePreparedGame(AtomicBoolean cancellation) throws Exception { return false; }
    /** Worker-only, once after resource sessions and failure cleanup have exited.
     * Backend subclasses use the exact worker ticket to release preparation;
     * an absent gateway does not imply an import/publish writer has stopped.
     */
    protected void preparationWorkerFinished() { }
    protected final void preparationStatus(final String message) {
        runOnUiThread(new Runnable() { public void run() { if (!dead) status.setText(message); }});
    }
    protected final boolean gameHandedOff() { return gameHandedOff; }
    /** Called when this Activity dies before its successful game handoff. */
    protected void preparationAbandoned() { }
    protected void launchGame() {
        Intent game = new Intent(getIntent());
        // Match the stock ProtocolLauncher handoff while retaining extras/data.
        game.setAction(null);
        game.removeCategory(Intent.CATEGORY_LAUNCHER);
        game.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        game.setClassName(getPackageName(), "com.netease.qrzd.Client");
        startActivity(game); gameHandedOff = true; finish();
    }
    @Override protected void onActivityResult(int request, int result, Intent data) {
        super.onActivityResult(request, result, data);
        if (request == PICK && result == RESULT_OK && data != null && data.getData() != null) {
            Uri uri = data.getData();
            try { getContentResolver().takePersistableUriPermission(uri, data.getFlags() & Intent.FLAG_GRANT_READ_URI_PERMISSION); }
            catch (SecurityException ignored) { /* Some providers allow this session only. */ }
            run(uri, true);
        }
    }
    @Override public void onBackPressed() { if (busy) cancelled.set(true); else super.onBackPressed(); }
    @Override protected void onDestroy() {
        dead = true; cancelled.set(true);
        try { if (!gameHandedOff) preparationAbandoned(); }
        finally { super.onDestroy(); }
    }
}
