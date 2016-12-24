package com.example.ladenheim.beerratings;

import android.os.AsyncTask;
import android.text.Html;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.SocketTimeoutException;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.RunnableFuture;
import java.util.concurrent.SynchronousQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Created by ladenheim on 10/5/16.
 */
public class ApiUtils {

    private static final int CONNECTION_TIMEOUT_MS = 60000;
    private static final int READ_TIMEOUT_MS = 60000;
    private static String LOG_TAG = ApiUtils.class.getSimpleName();
    private static String baseUrl = "https://www.beermenus.com";

    private static String baBaseUrl = "https://www.beeradvocate.com";

    private static String beerRatingUrl = "https://beer-rating.appspot.com";

    public static String getFirstMatch(String html, String pattern) {
        Pattern p = Pattern.compile(pattern);
        Matcher m = p.matcher(html);

        String result = "";
        while(m.find()) {
            result =  m.group(1);
            break;
        }
        return result;
    }

    public static String getRequest(String url) throws IOException {
        URLConnection conn = new URL(url).openConnection();
        conn.setConnectTimeout(CONNECTION_TIMEOUT_MS);
        conn.setReadTimeout(READ_TIMEOUT_MS);
        InputStream inputStream = conn.getInputStream();

        BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream, "UTF-8"));
        StringBuilder result = new StringBuilder();
        String line;
        while((line = reader.readLine()) != null ) {
            result.append(line);
        }
        return result.toString();

    }

    private static String scrapePlaceUrl(String html) {
        Pattern p = Pattern.compile("<a data-screen-title=(.*?)>");
        Matcher m = p.matcher(html);
        String placeHtml = "";
        while(m.find()) {
            placeHtml = m.group();
            break;
        }

        // No place matches, probably throw an error here.
        if(placeHtml == null) {
            return null;
        }

        int start = placeHtml.indexOf("href=\"") + 7;
        int end = placeHtml.indexOf("\">");
        return placeHtml.substring(start, end);
    }

    private static List<Beer> getBeerFromBeermenus(String searchVal) throws IOException {

        List<Beer> beers = new ArrayList<Beer>();

        String request = beerRatingUrl + "/place/" + URLEncoder.encode(searchVal, "UTF-8");
        String response = "";
        try {
            response = getRequest(request);
        }
        catch(SocketTimeoutException ex) {
            Log.d(LOG_TAG, "Response timed out with connection_timeout=%s" + CONNECTION_TIMEOUT_MS +
                    " and read_timeout=" + READ_TIMEOUT_MS);
            return beers;
        }
        try {
            JSONArray beerNamesJson = new JSONArray(response);
            for(int i=0; i < beerNamesJson.length(); i++) {
                beers.add(new Beer(beerNamesJson.getString(i)));
            }
        }
        catch (JSONException ex) {
            Log.d(LOG_TAG, "JSON exception: " + ex.getMessage());
            return beers;
        }

        return beers;
    }

    private static void getBeerAdvocateRatings(List<Beer> beers) throws IOException {
        ExecutorService es = Executors.newFixedThreadPool(75);
        for(Beer b: beers) {
            es.execute(new SetBeerRating(b, beerRatingUrl));
        }
        long start = System.currentTimeMillis() / 1000l;
        // Shutdown thread pool from accepting new tasks and wait for current ones to finish.
        es.shutdown();
        try {
            // Wait a while for existing tasks to terminate
            if (!es.awaitTermination(30, TimeUnit.SECONDS)) {
                es.shutdownNow(); // Cancel currently executing tasks
                // Wait a while for tasks to respond to being cancelled
                if (!es.awaitTermination(30, TimeUnit.SECONDS))
                    System.err.println("Pool did not terminate");
            }
        } catch (InterruptedException ie) {
            // (Re-)Cancel if current thread also interrupted
            es.shutdownNow();
            // Preserve interrupt status
            Thread.currentThread().interrupt();
        }
        Log.d(LOG_TAG, "Time used for query: " + (System.currentTimeMillis() / 1000l - start));
    }

    public static List<Beer> getBeers(String searchVal) throws IOException  {

        List<Beer> beers = getBeerFromBeermenus(searchVal);

        getBeerAdvocateRatings(beers);

        return beers;
    }
}


class SetBeerRating implements Runnable {

    private static String LOG_TAG = ApiUtils.class.getSimpleName();
    private Beer b;
    private String beerRatingUrl;

    public SetBeerRating(Beer b, String beerRatingUrl) {
        this.b = b;
        this.beerRatingUrl = beerRatingUrl;
    }

    @Override
    public void run() {
        try {
            String rating = ApiUtils.getRequest(beerRatingUrl + "/beer/" + b.name);
            b.ratingBeerAdvocate = Double.parseDouble(rating);
            Log.d(LOG_TAG, "Beer " + b.name + " has rating " + b.ratingBeerAdvocate);
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }
}