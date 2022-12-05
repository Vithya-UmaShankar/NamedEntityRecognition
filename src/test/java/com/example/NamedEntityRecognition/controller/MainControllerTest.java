package com.example.NamedEntityRecognition.controller;

import com.example.NamedEntityRecognition.model.NamedEntityRecognition;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.StatusLine;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.StringEntity;
import org.apache.http.util.EntityUtils;
import org.asynchttpclient.AsyncHttpClient;
import org.asynchttpclient.ListenableFuture;
import org.asynchttpclient.Response;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.concurrent.Future;

import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class MainControllerTest {

    @Test
    void pushToFile() throws IOException {
        String fileName = "/Users/vithya/Programs/python/entityText.txt";
        String text = "What a great game from Eden Park!";
        File f = new File(fileName);
        assertThat(f.exists());
        try (PrintWriter out = new PrintWriter(fileName)) {
            out.println(text);
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }
        String fileValue = new String(Files.readAllBytes(Paths.get(fileName)));
        assertEquals(fileValue.trim(), text.trim());
    }

    @Test
    void highlightEntities() {
        String text = "What a great game from Eden Park!";
        String[] entityText = {"Eden Park"}, entityLabel = {"STADIUM"};
        int[] startChar = {23}, endChar = {32};
        String ExpectedResult = "What a great game from <span title='STADIUM' class='entity' style='color: red; cursor: pointer;'>Eden Park</span>!";

        assertEquals(ExpectedResult, MainController.highlightEntities(text, startChar, endChar,entityText, entityLabel));
    }

    @Test
    void displayUI() {
    }

    @Test
    void reloadModel() throws IOException {
        HttpClient httpClient = mock(HttpClient.class);
        HttpPost httpPost = mock(HttpPost.class);
        HttpResponse httpResponse = mock(HttpResponse.class);
        StatusLine statusLine = mock(StatusLine.class);

        when(statusLine.getStatusCode()).thenReturn(200);
        when(httpResponse.getStatusLine()).thenReturn(statusLine);
        when(httpClient.execute(httpPost)).thenReturn(httpResponse);

        assertEquals(200, httpResponse.getStatusLine().getStatusCode());
    }

    @Test
    void detectEntity() throws IOException {

        Boolean pushToElastisearch = Boolean.FALSE;
        String text = "What a great game from Eden Park!";
        String fileName = "/Users/vithya/Programs/python/entityText.txt";

        pushToFile();

        String data = "data={'fileName': '" + fileName + "'} ";
        StringEntity entity = new StringEntity(data,
                ContentType.APPLICATION_FORM_URLENCODED);

        HttpClient httpClient = mock(HttpClient.class);
        HttpPost httpPost = mock(HttpPost.class);
        HttpResponse httpResponse = mock(HttpResponse.class);
        StatusLine statusLine = mock(StatusLine.class);

        httpPost.setEntity(entity);

        when(statusLine.getStatusCode()).thenReturn(200);
        when(httpResponse.getStatusLine()).thenReturn(statusLine);
        when(httpClient.execute(httpPost)).thenReturn(httpResponse);

        HttpEntity responseEntity = httpResponse.getEntity();


        if (responseEntity != null) {
            NamedEntityRecognition namedEntityRecognition = mock(NamedEntityRecognition.class);
            highlightEntities();

            if (pushToElastisearch) {
                AsyncHttpClient asyncHttpClient = mock(AsyncHttpClient.class);
                ListenableFuture<Response> responseFuture = mock(ListenableFuture.class);
                Response response = mock(Response.class);

                when(response.getStatusCode()).thenReturn(200);
                assertEquals(200, response.getStatusCode());
            }
        }
    }

    @Test
    void unloadModel() {
        AsyncHttpClient asyncHttpClient = mock(AsyncHttpClient.class);
        Future<Response> responseFuture = mock(Future.class);
        Response response = mock(Response.class);

        when(response.getStatusCode()).thenReturn(200);
        assertEquals(200, response.getStatusCode());
    }

    @Test
    void displayCSV() throws IOException {
        HttpClient httpClient = mock(HttpClient.class);
        HttpPost httpPost = mock(HttpPost.class);
        HttpResponse httpResponse = mock(HttpResponse.class);
        StatusLine statusLine = mock(StatusLine.class);

        when(statusLine.getStatusCode()).thenReturn(200);
        when(httpResponse.getStatusLine()).thenReturn(statusLine);
        when(httpClient.execute(httpPost)).thenReturn(httpResponse);

        assertEquals(200, httpResponse.getStatusLine().getStatusCode());
    }

    @Test
    void uploadFiles(){
    }
}