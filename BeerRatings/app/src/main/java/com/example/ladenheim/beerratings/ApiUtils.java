package com.example.ladenheim.beerratings;

import android.support.annotation.NonNull;
import android.text.Html;
import android.util.Log;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.SocketTimeoutException;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;
import java.util.ListIterator;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Created by ladenheim on 10/5/16.
 */
public class ApiUtils {

    private static final int CONNECTION_TIMEOUT_MS = 15000;
    private static final int READ_TIMEOUT_MS = 5000;
    private static String LOG_TAG = ApiUtils.class.getSimpleName();
    private static String baseUrl = "https://www.beermenus.com";

    private static String baBaseUrl = "https://www.beeradvocate.com";

    private static String getFirstMatch(String html, String pattern) {
        Pattern p = Pattern.compile(pattern);
        Matcher m = p.matcher(html);

        String result = "";
        while(m.find()) {
            result =  m.group(1);
            break;
        }
        return result;
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

    private static List<Beer> getBeerFromBeermenus(String html) {;
        Pattern p = Pattern.compile("<h3 class=\"mb-0\">(.*?)</h3>");
        Matcher m = p.matcher(html);
        List<Beer> beers = new ArrayList<Beer>();

        while(m.find()) {
            Beer b = new Beer();
            b.name = Html.fromHtml(m.group(1).trim()).toString();
            beers.add(b);
        }
        return beers;
    }

    private static void getBeerAdvocateRatings(List<Beer> beers) throws IOException {

        for(Beer b: beers) {
            String request = baBaseUrl + "/search/?qt=beer&q=" + URLEncoder.encode(b.name, "UTF-8");

            String responseHtml = getRequest(request);
            String beerUrl = getFirstMatch(responseHtml, "<a href=\"(/beer/profile/.*?)\">");

            String beerResponseHtml = getRequest(baBaseUrl + beerUrl);
            String s = getFirstMatch(
                    beerResponseHtml, "<span class=\"BAscore_big ba-score\">(.*?)</span>");
            if(s.equals("-") || s.equals("")) {
                s = "0";
            }
            b.ratingBeerAdvocate = Double.parseDouble(s);
            Log.d(LOG_TAG, "Beer " + b.name + " has rating " + b.ratingBeerAdvocate);
        }

    }

    public static List<Beer> getBeers(String searchVal) throws IOException  {
        // searchVal = "bruno pizza";
        String request = baseUrl + "/search?q=" + URLEncoder.encode(searchVal, "UTF-8");
        String response = "";
        try {
            response = getRequest(request);
        }
        catch(SocketTimeoutException ex) {
            Log.d(LOG_TAG, "Response timed out with connection_timeout=%s" + CONNECTION_TIMEOUT_MS +
                    " and read_timeout=" + READ_TIMEOUT_MS);
        }

        String placeUrl = scrapePlaceUrl(response);
        String placeResponse = getRequest(baseUrl + "/" + placeUrl);
        List<Beer> beers = getBeerFromBeermenus(placeResponse);

        getBeerAdvocateRatings(beers);

        return beers;
    }

    private static String getRequest(String url) throws IOException {
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


}
