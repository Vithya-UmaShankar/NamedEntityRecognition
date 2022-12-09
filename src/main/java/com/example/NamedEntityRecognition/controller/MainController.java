package com.example.NamedEntityRecognition.controller;

import com.example.NamedEntityRecognition.model.NamedEntityRecognition;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.util.EntityUtils;
import org.asynchttpclient.AsyncHttpClient;
import org.asynchttpclient.Dsl;
import org.asynchttpclient.ListenableFuture;
import org.asynchttpclient.Request;
import org.asynchttpclient.Response;
import org.asynchttpclient.AsyncCompletionHandler;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;

@Controller
@Slf4j
public class MainController {

    private static Logger logger = LoggerFactory.getLogger(MainController.class);
    public String APP_PATH = "/Users/vithya/Programs/Springboot/InnectoToken/" + "NamedEntityRecognition/Python/";
    HttpClient httpClient = HttpClientBuilder.create().build();
    AsyncHttpClient asyncHttpClient = Dsl.asyncHttpClient();
    String activeTab = "Extract";
    String recognizedEntities = null;
    String inputText = null;
    String[] fileNames = null;

    /**
     * Put the passed text into a file
     * @param fileName Name of the file which will have the text
     * @param text Input text
     */
    public void pushToFile(String fileName, String text) {
        try (PrintWriter out = new PrintWriter(fileName)) {
            out.println(text);
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }
    }

    /**
     * Used to mark the entities with a highlighted color. Displays the label of the entity as the tag title
     * @param text Input text
     * @param startChar List of int. Denotes the starting index of recognized entities
     * @param endChar List of int. Denotes the ending index of recognized entities
     * @param entityText List of String. Denotes the recognized entities
     * @param entityLabel List of String. Denotes the labels of recognized entities
     * @return The text with highlighted entities
     */
    public static String highlightEntities(String text, int[] startChar, int[] endChar, String[] entityText, String[] entityLabel) {
        String highlightedEntity = "";

        if (startChar.length != 0) {
            for (int i = 0; i < startChar.length; i++) {
                if (i == 0 && startChar[i] != 0) highlightedEntity = text.substring(0, startChar[i]);
                else if (i == 0 && startChar[i] == 0) highlightedEntity = "";
                else highlightedEntity += text.substring(endChar[i - 1], startChar[i]);
                highlightedEntity += "<span title='" + entityLabel[i] + "' class='entity' style='color: red; cursor: pointer;'>";
                highlightedEntity += text.substring(startChar[i], endChar[i]);
                highlightedEntity += "</span>";

            }
            highlightedEntity += text.substring(endChar[endChar.length - 1]);

            highlightedEntity = highlightedEntity.replace("\n", "<br>");
        }
        return highlightedEntity;
    }

    /**
     * Displays the entityRecognition.html file
     * @param model An object of Model class
     * @return The webpage
     */
    @GetMapping("/api/v1/detectEntity")
    public String displayUI(Model model) throws IOException {

        model.addAttribute("activeTab", activeTab);
        if (activeTab == "Display") {
            model.addAttribute("fileNames", fileNames);
        }
        if (activeTab == "Upload") {
            model.addAttribute("uploaded", "True");
        }
        if (activeTab == "Extract" && recognizedEntities != null) {
            model.addAttribute("inputText", inputText);
            model.addAttribute("entities", recognizedEntities);
        }

        String[] fileNamesLabel = {"Players", "Cities", "Stadiums", "Organizations", "Batting", "Bowling", "Teams"};
        model.addAttribute("fileNamesLabel", fileNamesLabel);

        return "entityRecognition";
    }

    /**
     * Used to reload the NamedEntityRecognition tensorflow model
     * @param model An object of Model class
     * @return entityRecognition.html
     * @throws IOException
     */
    @GetMapping("/api/v1/reload")
    public String reloadModel(Model model) throws IOException {

        HttpPost request = new HttpPost("http://127.0.0.1:5000/reload?sport=Cricket");

        HttpResponse response = httpClient.execute(request);

        if (response.getStatusLine().getStatusCode() == 200) {
            return "redirect:/api/v1/detectEntity";
        } else {
            return "error";
        }

    }

    /**
     * Used to detect entities in a given text
     * @param detectEntityText The input text
     * @param model An object of Model class
     * @return entityRecognition.html
     * @throws IOException
     * @throws InterruptedException
     * @throws ExecutionException
     */
    @PostMapping("/api/v1/detectEntity")
    public String detectEntity(
            @RequestParam("detectEntityText") String detectEntityText,
            Model model) throws IOException, InterruptedException, ExecutionException {

        activeTab = "Extract";
        Boolean pushToElastisearch = Boolean.TRUE;
        String fileName = APP_PATH + "entityText.txt";

        pushToFile(fileName, detectEntityText);

        HttpPost request = new HttpPost("http://127.0.0.1:5000/extract?sport=Cricket");

        HttpResponse response = httpClient.execute(request);
        HttpEntity responseEntity = response.getEntity();
        String result = EntityUtils.toString(responseEntity);

        if (responseEntity != null) {
            ObjectMapper objectMapper = new ObjectMapper();
            NamedEntityRecognition namedEntityRecognition = objectMapper.readValue(result, NamedEntityRecognition.class);
            recognizedEntities = highlightEntities(namedEntityRecognition.getText(), namedEntityRecognition.getStartChar(), namedEntityRecognition.getEndChar(), namedEntityRecognition.getEntityText(), namedEntityRecognition.getEntityLabel());
            inputText = namedEntityRecognition.getText();

            if (pushToElastisearch && recognizedEntities != "") {

                Request request1 = Dsl.post("http://127.0.0.1:5000/elastic?sport=Cricket")
                        .addFormParam("data", result)
                        .build();
                ListenableFuture<Integer> f = null;
                f = asyncHttpClient.executeRequest(request1,
                        new AsyncCompletionHandler<Integer>() {
                            @Override
                             public Integer onCompleted(Response response) throws Exception {
                                // Do something with the Response
                                return response.getStatusCode();
                            }
                            @Override
                            public void onThrowable(Throwable t) {
                                // Something wrong happened.
                                t.printStackTrace();
                            }
                        });
                int statusCode;
                if (f != null) {
                    try {
                        statusCode = f.get();
                        if (statusCode == 200) {
                            logger.info("");
                        }
                    } catch (Exception ex) {
                        ex.printStackTrace();
                        return "error"; //something went wrong while displaying entity
                    }
                }
            }
            return "redirect:/api/v1/detectEntity";//success return back entity to highlight
        }

        return "redirect:/api/v1/detectEntity"; //No entity detected
    }

    /**
     * Used to unload the NamedEntityRecognition tensorflow model from memory
     * @param model An object of Model class
     * @return entityRecognition.html
     * @throws ExecutionException
     * @throws InterruptedException
     */
    @GetMapping("/api/v1/clearCache")
    public String unloadModel(Model model) throws ExecutionException, InterruptedException {

        Request request = Dsl.get("http://127.0.0.1:5000/terminate?sport=Cricket").build();
        // Basic Async
        Future<Response> responseFuture = asyncHttpClient.executeRequest(request);
        Response response = responseFuture.get();
        if (response.getStatusCode() == 200) {
            return "redirect:/api/v1/detectEntity";
        } else {
            return "error";
        }
    }

    /**
     * Used to display a snapshot of all the training files
     * @param model An object of Model class
     * @return entityRecognition.html
     * @throws IOException
     */
    @PostMapping("/api/v1/display")
    public String displayCSV(Model model) throws IOException {
        activeTab = "Display";
        HttpPost request = new HttpPost("http://127.0.0.1:5000/display?sport=Cricket");
        HttpResponse response = httpClient.execute(request);
        String result = "";

        if (response.getStatusLine().getStatusCode() == 200) {
            result = EntityUtils.toString(response.getEntity());
            result = result
                    .replace("[", "")
                    .replace("]", "")
                    .replace("\"", "")
                    .replace(" ", "");
            fileNames = result.split(",");
        }
        return "redirect:/api/v1/detectEntity";
    }

    /**
     * Used to upload all the training files
     * @param files A list of MultipartFile
     * @param model An object of Model class
     * @return entityRecognition.html
     * @throws IOException
     */
    @PostMapping("/api/v1/uploadFiles")
    public String uploadFiles(@RequestParam("files") MultipartFile[] files, Model model) throws IOException {

        activeTab = "Upload";
        String upload_dir = APP_PATH + "CSV/Cricket/";
        for (int i = 0; i < files.length; i++) {
            String fileName = StringUtils.cleanPath(files[i].getOriginalFilename());// normalize the file path
            Path pathTarget = Paths.get(upload_dir + fileName);
            Files.copy(files[i].getInputStream(), pathTarget, StandardCopyOption.REPLACE_EXISTING);
        }
        return "redirect:/api/v1/detectEntity";
    }
}
