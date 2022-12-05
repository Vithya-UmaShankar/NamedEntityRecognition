package com.example.NamedEntityRecognition.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
/**
 * Used to convert the JSON value sent by python into an object
 */
public class NamedEntityRecognition {
    String text;
    int[] startChar;
    int[] endChar;
    String[] entityText;
    String[] entityLabel;
}
