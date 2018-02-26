package com.zhauniarovich.bbtester;

import android.app.Activity;
import android.app.Application;
import android.app.Instrumentation;
import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.Looper;
import android.os.Message;
import android.util.Log;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;

/**
 * Created by yury on 17/02/18.
 */

public class EmmaInstrumentation extends Instrumentation {
    private static final String TAG = "EmmaInstrumentation";
//    private static final boolean LOGD = true;

    private static final int MSG_GENERATE_COVERAGE = 1;
    private static final int MSG_REPORT_EXCEPTION = 2;
    private static final int MSG_REMOVE_REPORT_DIR = 3;
    private static final int MSG_FINISH_WRITER_OPERATIONS = 4;

    private static final int MSG_FINISH_INSTRUMENTATION = 11;

    private final static String DEFAULT_REPORT_ROOTDIR = "/mnt/sdcard";
    private static final String ERRORS_FILENAME = "errors.txt";
//    private static final int SHELL_UID = android.os.Process.getUidForName("shell");

    private static final String ACTION_FINISH_TESTING = "com.zhauniarovich.bbtester.finishtesting";

    private static final String PREFIX_ONSTOP = "onstop";
    private static final String PREFIX_ONERROR = "onerror";


    private static final String KEY_COVERAGE = "coverage";
    private static final String KEY_PROCEED_ON_ERROR = "proceedOnError";
    private static final String KEY_GENERATE_COVERAGE_REPORT_ON_ERROR = "generateCoverageReportOnError";
    private static final String KEY_REPORT_FOLDER = "coverageDir";
    private static final String KEY_CANCEL_ANALYSIS = "cancelAnalysis";

    private boolean mCoverage = true;
    private boolean generateCoverageOnError = true;
    private boolean proceedOnError = false;
    private boolean cancelAnalysis = false;

    private File reportDir = null;
    private File errorFile = null;
    private File lockFile = null;

    private static int errorCounter = 0;
    private static String targetPackageName;

    private HandlerThread ht;
    private Handler mUiHandler;
    private Handler mWriterThreadHandler;

    /**
     * Constructor
     */
    public EmmaInstrumentation() {
        super();
        // Log.d(TAG, "Constructor. Thread: " + Thread.currentThread().getName());
    }

    @Override
    public void onCreate(Bundle arguments) {
        super.onCreate(arguments);
        Log.d(TAG, "onCreate: Obtained instrumentation intent: " + arguments.toString());

//        targetPackageName = getTargetContext().getPackageName();
        targetPackageName = getComponentName().getPackageName();

        mCoverage = getBooleanArgument(arguments, KEY_COVERAGE, true);
        proceedOnError = getBooleanArgument(arguments, KEY_PROCEED_ON_ERROR, true);
        generateCoverageOnError = getBooleanArgument(arguments, KEY_GENERATE_COVERAGE_REPORT_ON_ERROR, false);

        final String reportDirParentPth = arguments.getString(KEY_REPORT_FOLDER, DEFAULT_REPORT_ROOTDIR);
        //getting lock for a file
        lockFile = new File(reportDirParentPth, targetPackageName + ".lock");
        if (!lockFile.exists()) {
            try {
                lockFile.createNewFile();
            } catch (IOException e) {
                // TODO: Automatically generated
                e.printStackTrace();
            }
        }
        else {
            Log.e(TAG,"Lock file exists for some reason. Exiting instrumentation!");
            finish(Activity.RESULT_CANCELED, "Lock file exists for some reason. Exiting instrumentation!");
            return;
        }

        errorFile = new File(reportDir, ERRORS_FILENAME);
        reportDir = new File(reportDirParentPth, targetPackageName);
        boolean success = reportDir.mkdirs();
        Log.i(TAG, success ? "The report dir is created!" : "The report dir is NOT created!");

        ht = new HandlerThread("WriterThread");
        ht.start();
        mWriterThreadHandler = new Handler(ht.getLooper(), writerThreadHandlerCallback);
        mUiHandler = new Handler(uiThreadHandlerCallback);

        IntentFilter iFilter = new IntentFilter(ACTION_FINISH_TESTING);
        getContext().registerReceiver(mMessageReceiver, iFilter);

        start();
        Log.d(TAG, "onCreate: After start!");
    }


    @Override
    public void onStart() {
        super.onStart();
        Log.d(TAG, "Starting instrumentation. Thread: " + Thread.currentThread().getName());
        Looper.prepare(); //do we really need this?
    }


    @Override
    public boolean onException(Object obj, Throwable e) {
        Log.d(TAG, "onException: AUT exception caught!");

        long currentTimeMillis = System.currentTimeMillis();
        String coverageFileName = PREFIX_ONERROR + "_coverage_" + String.valueOf(currentTimeMillis) + ".ec";

        if (generateCoverageOnError) {
            Message msg = Message.obtain(mWriterThreadHandler, MSG_GENERATE_COVERAGE);
            msg.obj = coverageFileName;
            msg.sendToTarget();
        }

        Message msg = Message.obtain(mWriterThreadHandler, MSG_REPORT_EXCEPTION);
        msg.obj = compileExceptionMessage(currentTimeMillis, coverageFileName, obj, e);
        msg.sendToTarget();

        //true - continue to execute tests, false - let the exception to be fired
        return proceedOnError;
    }


    private void finish(int resultCode, String resultMsg) {
        Bundle results = new Bundle();
        results.putString(Instrumentation.REPORT_KEY_IDENTIFIER, EmmaInstrumentation.class.getName());
        results.putString(Instrumentation.REPORT_KEY_STREAMRESULT, resultMsg);
        finish(resultCode, results);
    }


    @Override
    public void finish(int resultCode, Bundle results) {
        Log.d(TAG, "Finishing instrumentation. ResultCode: " + resultCode + " Results: " + results.toString());
        if ((lockFile != null) && (lockFile.exists())) {
            Log.d(TAG, "finish: Removing lockFile...");
            lockFile.delete();
        }
        super.finish(resultCode, results);
    }


    @Override
    public void onDestroy() {
        Log.d(TAG, "OnDestroy. Thread: " + Thread.currentThread().getName());
        getContext().unregisterReceiver(mMessageReceiver);
        ht.getLooper().quitSafely();
        super.onDestroy();
    }


    private String compileExceptionMessage(long timeMillis, String coverageFileName, Object obj, Throwable e) {
        String errorComp;
        if (obj == null) {
            errorComp = "null";
        }
        else if (obj instanceof Application) {
            errorComp = "Application";
        }
        else if (obj instanceof Activity) {
            errorComp = "Activity";
        }
        else if (obj instanceof Service) {
            errorComp = "Service";
        }
        else if (obj instanceof BroadcastReceiver) {
            errorComp = "BroadcastReceiver";
        }
        else {
            errorComp = obj.getClass().getSimpleName();
        }

        String errorSource = "null";
        if (obj != null) {
            errorSource = obj.getClass().getName();
        }

        StringBuffer exceptionStringBuffer = new StringBuffer();
        exceptionStringBuffer.append("ErrorCount: ").append(errorCounter++).append("\n");
        exceptionStringBuffer.append("Time: ").append(timeMillis).append("\n");
        exceptionStringBuffer.append("CoverageFile: ").append(coverageFileName != null ? coverageFileName : "").append("\n");
        exceptionStringBuffer.append("PackageName: ").append(targetPackageName).append("\n");
//        exceptionStringBuffer.append("ProcessPid: ").append(Process.myPid()).append("\n"); //could be another process
        exceptionStringBuffer.append("ErrorComponent: ").append(errorComp).append("\n");
        exceptionStringBuffer.append("ErrorSource: ").append(errorSource).append("\n");
        exceptionStringBuffer.append("ShortMsg: ").append(e.toString()).append("\n");
        exceptionStringBuffer.append("LongMsg: ").append(e.getMessage()).append("\n");
        exceptionStringBuffer.append("Stack: \n").append(getStackTrace(e)).append("\n");
//		exceptionStringBuffer.append("------------------------------------------------------------").append("\n");
//		exceptionStringBuffer.append("THREAD_STATE: \n").append(getThreadState()).append("\n");
        exceptionStringBuffer.append("============================================================").append("\n\n");

        return exceptionStringBuffer.toString();
    }


    private String getStackTrace(Throwable e) {
        StringWriter sw = new StringWriter();
        PrintWriter pw = new PrintWriter(sw);
        e.printStackTrace(pw);
        return sw.toString(); // stack trace as a string;
    }


    private boolean getBooleanArgument(Bundle arguments, String tag, boolean defaultValue) {
        String tagString = arguments.getString(tag);
        return tagString == null ? defaultValue : Boolean.parseBoolean(tagString);
    }


//	private static String getThreadState() {
//		Set<Map.Entry<Thread, StackTraceElement[]>> threads = Thread.getAllStackTraces().entrySet();
//		StringBuilder threadState = new StringBuilder();
//		for (Map.Entry<Thread, StackTraceElement[]> threadAndStack : threads) {
//			StringBuilder threadMessage = new StringBuilder("  ").append(threadAndStack.getKey());
//			threadMessage.append("\n");
//			for (StackTraceElement ste : threadAndStack.getValue()) {
//				threadMessage.append("    ");
//				threadMessage.append(ste.toString());
//				threadMessage.append("\n");
//			}
//			threadMessage.append("\n");
//			threadState.append(threadMessage.toString());
//		}
//		return threadState.toString();
//	}


    /**
     * BroadcastReceiver handler for intent sending to finish testing of application.
     */
    private final BroadcastReceiver mMessageReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            // TODO: Check this code later
            //checking that the intent is sent from the adb shell
//    		final int callingUid = Binder.getCallingUid();
//    		if (callingUid != SHELL_UID) {
//    			return;
//    		}
            Log.d(TAG, "Broadcast received in the thread: " + Thread.currentThread().getName());

            final Bundle arguments = intent.getExtras();
            if (arguments != null) {
                cancelAnalysis = arguments.getBoolean(KEY_CANCEL_ANALYSIS, false);
            }

            if (cancelAnalysis) {
                Message rMsg = Message.obtain(mWriterThreadHandler, MSG_REMOVE_REPORT_DIR);
                rMsg.sendToTarget();
                Message fMsg = Message.obtain(mWriterThreadHandler, MSG_FINISH_WRITER_OPERATIONS);
                fMsg.sendToTarget();
                return;
            }

            if (mCoverage) {
                final long currentTime = System.currentTimeMillis();
                String coverageFileName = PREFIX_ONSTOP  + "_coverage_" + String.valueOf(currentTime) + ".ec";
                Message msg = Message.obtain(mWriterThreadHandler, MSG_GENERATE_COVERAGE);
                msg.obj = coverageFileName;
                msg.sendToTarget();
            }

            Message fMsg = Message.obtain(mWriterThreadHandler, MSG_FINISH_WRITER_OPERATIONS);
            fMsg.sendToTarget();
        }
    };



    private final Handler.Callback uiThreadHandlerCallback = new Handler.Callback() {
        @Override
        public boolean handleMessage(Message msg) {
            switch (msg.what) {
                case MSG_FINISH_INSTRUMENTATION: {
                    int resultCode = msg.arg1;
                    String resultMsg = (String) msg.obj;
                    finish(resultCode, resultMsg);
                    break;
                }
            }

            return false;
        }
    };


    private final Handler.Callback writerThreadHandlerCallback = new Handler.Callback() {
        @Override
        public boolean handleMessage(Message msg) {
            switch (msg.what) {
                case MSG_GENERATE_COVERAGE: {
                    Log.d(TAG, "handleMessage: Got MSG_GET_COVERAGE");
                    String coverageFileName = (String) msg.obj;
                    generateCoverageReport(coverageFileName);
                    break;
                }
                case MSG_REPORT_EXCEPTION: {
                    Log.d(TAG, "handleMessage: Got MSG_REPORT_EXCEPTION");
                    String exceptionMessage = (String) msg.obj;
                    appendException(exceptionMessage);
                    break;
                }
                case MSG_REMOVE_REPORT_DIR: {
                    Log.d(TAG, "handleMessage: Got MSG_REMOVE_REPORT_DIR");
                    removeDirectory(reportDir);
                    break;
                }
                case MSG_FINISH_WRITER_OPERATIONS: {
                    Log.d(TAG, "handleMessage: Got MSG_FINISH_WRITER_OPERATIONS");
                    sendFinishInstrumentationMsg(Activity.RESULT_OK, "Instrumentation done!");
                    break;
                }
            }
            return false;
        }


        private void generateCoverageReport(String filename) {
            if (LOGD) {
                Log.d(TAG, "");
            }
            java.io.File coverageFile = new java.io.File(reportDir, filename);
            if (LOGD)
                Log.d(TAG, "generateCoverageReport(): " + coverageFile.getAbsolutePath());
            // We may use this if we want to avoid reflection and we include
            // emma.jar
            // RT.dumpCoverageData(coverageFile, false, false);

            // Use reflection to call emma dump coverage method, to avoid
            // always statically compiling against emma jar
            try {
                Class<?> emmaRTClass = Class.forName("com.vladium.emma.rt.RT");
                Method dumpCoverageMethod = emmaRTClass.getMethod("dumpCoverageData",
                        coverageFile.getClass(), boolean.class, boolean.class);
                dumpCoverageMethod.invoke(null, coverageFile, false, false);
                Log.e(TAG, "generateCoverageReport: ok");

            } catch (ClassNotFoundException e) {
                reportEmmaError("Is emma jar on classpath?", e);
            } catch (SecurityException e) {
                reportEmmaError("SecurityException", e);
            } catch (NoSuchMethodException e) {
                reportEmmaError("NoSuchMethodException",e);
            } catch (IllegalArgumentException e) {
                reportEmmaError("IllegalArgumentException", e);
            } catch (IllegalAccessException e) {
                reportEmmaError("IllegalAccessException", e);
            } catch (InvocationTargetException e) {
                reportEmmaError("InvocationTargetException",e);
            } catch (Exception e){
                reportEmmaError("Exception", e);
            }
        }


        private void reportEmmaError(String hint, Exception e) {
            String errorMsg = "Failed to generate emma coverage. " + hint + "\n" + e.toString();
            Log.e(TAG, errorMsg);
            sendFinishInstrumentationMsg(Activity.RESULT_CANCELED, errorMsg);
        }


        private void sendFinishInstrumentationMsg(int resultCode, String resultMsg) {
            Message msg = Message.obtain(mUiHandler, MSG_FINISH_INSTRUMENTATION);
            msg.arg1 = resultCode;
            msg.obj =  resultMsg;
            msg.sendToTarget();
        }


        private void appendException(String exceptionString) {
            Log.d(TAG, "appendException: Appending exception");
            try {
                if (!errorFile.exists()) {
                    errorFile.createNewFile();
                }
                FileWriter fileWriter = new FileWriter(errorFile, true);
                BufferedWriter bufferWriter = new BufferedWriter(fileWriter);
                bufferWriter.write(exceptionString);
                bufferWriter.close();
            }
            catch (IOException e) {
                Log.e(TAG, "appendException: Strange error!", e);
                e.printStackTrace();
            }
        }


        private void removeDirectory(File dir) {
            if (dir.isDirectory()) {
                File[] files = dir.listFiles();
                if (files != null && files.length > 0) {
                    for (File aFile : files) {
                        removeDirectory(aFile);
                    }
                }
                dir.delete();
            } else {
                dir.delete();
            }
        }
    };
}
